import networkx as nx
import unicodedata
from selenium_utilities import open_site_selenium, get_driver_soup, maximize_the_window, close_driver
from log import log_function
import util
import classifier

def normalize_label(label):
    """Normalize node labels to ASCII and replace unsupported characters."""
    return ''.join(
        c if ord(c) < 128 else '?' for c in unicodedata.normalize('NFKD', label)
    )

def extract_all_attributes(tag):
    """Extract all attributes, text, and URLs from a tag."""
    attributes = {k: v for k, v in tag.attrs.items()}  # Keep all attributes

    # Extract partitioned text content based on child elements
    sections = []
    for child in tag.children:
        if isinstance(child, str):
            # Direct text content
            text = child.strip()
            if text:
                sections.append(text)
        elif child.name:
            # Text content from nested tags
            nested_text = child.get_text(strip=True)
            if nested_text:
                sections.append(nested_text)

    if sections:
        attributes['partitioned_text'] = sections  # Store partitioned text as a list

    # Extract href, src, and other URL-related attributes
    urls = []
    for key, value in tag.attrs.items():
        if key in ["href", "src", "data-url"] and isinstance(value, str):
            urls.append(value)
    if urls:
        attributes['urls'] = urls

    return attributes

def html_to_graph(soup):
    skippers = [
        'class', 'data-testid', 'height', 'width', 'aria-hidden',
        'style', 'loading', 'id', "viewbox", "aria-pressed", "aria-label", "role",
        'lang', "type",
    ]
    """Convert a BeautifulSoup object into a NetworkX directed graph."""
    graph = nx.DiGraph()

    # Recursive function to add nodes and edges
    def add_nodes_edges(tag, parent=None):
        try:
            if tag.name:
                label = normalize_label(tag.name)
                attributes = extract_all_attributes(tag)

                attribute_list_to_include = []

                for key, values in attributes.items():
                    if key in skippers:
                        continue
                    # Ensure values is a list
                    if not isinstance(values, list):
                        values = [values]

                    for value in values:
                        if not util.full_html_tag_check(value):
                            # This is not an HTML-like thing; we can add it to the node
                            attribute_list_to_include.append((key, value))

                # Check for conflicts with the 'label' key
                attribute_dict = dict(attribute_list_to_include)
                if 'label' not in attribute_dict:
                    attribute_dict['label'] = label  # Add the label if it's not already present

                # Add the node to the graph with filtered attributes
                graph.add_node(id(tag), **attribute_dict)  # Use id(tag) for unique node ID

                if parent:
                    graph.add_edge(id(parent), id(tag))  # Edge from parent to child

                for child in tag.children:
                    add_nodes_edges(child, tag)
        except Exception as e:
            print(f"[Error] {e}")
            print(tag)
            input("---")

    add_nodes_edges(soup)

    return graph

def extract_relevant_data_flat(descendants):
    """Extract and flatten meaningful data from descendants into a list."""
    flattened_data = []
    for descendant in descendants:
        label = descendant.get("label", "")
        # Include all meaningful attributes
        if label:
            filtered_descendant = {
                k: v
                for k, v in descendant.items()
                if k in {"label", "class", "href", "src", "text", "urls", "alt", "title", "data-pid", "value", "partitioned_text"}
            }
            flattened_data.append(filtered_descendant)
    return flattened_data

def calculate_children_count(graph, excluded_labels):
    """
    Calculate the number of children for each node, excluding certain labels,
    and remove nodes with fewer than 10 children or more than 200 children.
    Additionally, calculate the average amount of string data (from attributes) 
    in the children of each node, and skip nodes with an average below 20 chars.
    """
    # Configuration constants
    MAX_CHILDREN = 200
    MIN_CHILDREN = 10
    AVG_CHARS_MINIMUM = 20

    # Step 1: Filter out excluded nodes
    valid_nodes = []
    for node in graph.nodes:
        label = graph.nodes[node].get('label', 'Unknown')
        if label not in excluded_labels:
            valid_nodes.append(node)
            # print(f"Node: {node}, Label: {label}")  # Debug: Print each valid node and its label

    # Step 2: For each valid node, find its children and calculate average string data
    node_children = []
    avg_data_per_child = {}  # Store average data per child for each node

    for node in valid_nodes:
        children = [
            child for child in graph.successors(node)
            if graph.nodes[child].get('label', 'Unknown') != 'script'
        ]

        # Calculate the total string data from all attributes of all children
        total_data_length = 0
        for child in children:
            attributes = graph.nodes[child]  # Get all attributes of the child node
            for key, value in attributes.items():
                if isinstance(value, str):  # Only count string data
                    total_data_length += len(value)
                elif isinstance(value, list):  # If it's a list of strings, count their lengths
                    total_data_length += sum(len(str(v)) for v in value)

        # Calculate the average data length per child
        avg_chars = total_data_length / len(children) if children else 0

        # Skip nodes based on the constraints
        if MIN_CHILDREN <= len(children) <= MAX_CHILDREN and avg_chars >= AVG_CHARS_MINIMUM:
            avg_data_per_child[node] = avg_chars  # Store for later output
            node_children.append((node, len(children)))

    # Step 3: Sort nodes by the number of children in descending order
    node_children.sort(key=lambda x: x[1], reverse=True)

    '''
    # Step 4: Print a sample of the ranked nodes with average data per child
    print(f"Sample of ranked nodes (children between {MIN_CHILDREN} and {MAX_CHILDREN}, avg data >= {AVG_CHARS_MINIMUM} chars):")
    for node, count in node_children[:5]:
        avg_chars = avg_data_per_child.get(node, 0)
        print(f"Node: {node}, Children count: {count}, Avg data in children: {avg_chars:.2f} chars")

    print("excluded_labels:", excluded_labels)

    # Step 5: Return the sorted list of node children counts
    exit()  # Debugging stop point
    '''
    return node_children

def get_top_node_with_most_children(node_children_count, graph):
    """
    Get the node with the most children from the calculated list.
    """
    if not node_children_count:
        print("No valid nodes found that meet the criteria.")
        return None

    node_children_count.sort(key=lambda x: x[1], reverse=True)
    top_node, top_children_count = node_children_count[0]
    top_node_label = graph.nodes[top_node].get('label', 'Unknown')

    return top_node, top_children_count, top_node_label


def collect_child_details(graph, top_node):
    """
    Collect details about the children of the top node.
    """
    children_details = []

    for child in graph.successors(top_node):
        child_label = graph.nodes[child].get('label', 'Unknown')
        child_attrs = graph.nodes[child]
        grandchild_count = len(list(graph.successors(child)))

        descendant_attributes = [
            graph.nodes[desc] for desc in nx.descendants(graph, child)
        ]

        unique_descendants = sort_unique_descendants(descendant_attributes)

        # Flatten meaningful data
        relevant_flattened = extract_relevant_data_flat(unique_descendants)

        children_details.append({
            "label": child_label,
            "grandchildren_count": grandchild_count,
            "attributes": child_attrs,
            "flattened_relevant_data": relevant_flattened
        })

    return children_details


def sort_unique_descendants(descendant_attributes):
    """
    Sort and deduplicate descendant attributes for a node.
    """
    return sorted(
        {
            frozenset(
                (k, tuple(v) if isinstance(v, list) else v)  # Convert lists to tuples
                for k, v in item.items()
            ): item
            for item in descendant_attributes if isinstance(item, dict)
        }.values(),
        key=lambda x: x.get('label', 'Unknown')
    )


def calculate_total_descendants(graph, top_node):
    """
    Calculate the total number of descendants for the top node.
    """
    return len([desc for desc in nx.descendants(graph, top_node)])


def find_top_node_with_most_children(graph):
    """
    Main function to find the top node with the most children.
    """
    excluded_labels = {'select', 'body', 'head', 'svg', 'html'}

    node_children_count = calculate_children_count(graph, excluded_labels)

    top_node_info = get_top_node_with_most_children(node_children_count, graph)
    if top_node_info is None:
        return None
    top_node, top_children_count, top_node_label = top_node_info
    children_details = collect_child_details(graph, top_node)
    total_descendants = calculate_total_descendants(graph, top_node)


    return {
        "top_node": {
            "label": top_node_label,
            "children_count": top_children_count,
            "attributes": graph.nodes[top_node]
        },
        "children": children_details,
        "total_descendants": total_descendants
    }

def process_soup(soup):
    """Main function to process a BeautifulSoup object and return analysis."""
    # print("[process_soup] Processing soup into graph.")
    graph = html_to_graph(soup)
    node_with_most_children = find_top_node_with_most_children(graph)
    return node_with_most_children

def process_results(result):
    """Process and print the results from the top node analysis."""
    if not result:
        print("No valid nodes found in the graph.")
        return

    top_node = result["top_node"]
    
    all_data = []
    for child in result["children"]:
        child_data = []
        for i, flattened_item in enumerate(child["flattened_relevant_data"]):
            for key, value in flattened_item.items():
                if type(value) == list:
                    for j in value:
                        if j not in child_data:
                            if not util.full_html_tag_check(j):
                                child_data.append(j)

                else:
                    if value not in child_data:
                        if not util.full_html_tag_check(value):
                            child_data.append(value)

        all_data.append(child_data)
    return all_data

def remove_larger_strings(data, length_threshold=100):
    if data == None:
        print("NO DATA RETURN NONE")
        return []
    """
    Removes larger strings from a list of lists if they contain smaller strings 
    from the same sublist, unless their length exceeds the specified threshold.
    
    Parameters:
    - data: List of lists of strings.
    - length_threshold: Length above which larger strings are preserved.
    
    Returns:
    - List of lists with redundant larger strings removed.
    """
    cleaned_data = []

    for sublist in data:
        filtered_sublist = list(sublist)  # Create a copy of the sublist

        for string in sublist:
            for other_string in sublist:
                # Skip comparing a string with itself
                if string != other_string:
                    # If `string` is contained in `other_string` and `other_string` is not above the length threshold
                    if string in other_string and len(other_string) <= length_threshold:
                        # Remove the larger string
                        if other_string in filtered_sublist:
                            filtered_sublist.remove(other_string)

        cleaned_data.append(filtered_sublist)

    return cleaned_data

def full_conversion(soup):
    result = process_soup(soup)
    data = process_results(result)
    flattended_data = remove_larger_strings(data, length_threshold=100)

    final_classified_data = []
    for i in flattended_data:
        i_arr = []
        type_counter = {}  # Keeps track of counts for each type locally
        for j in i:
            j_type = classifier.classify(j)
            
            # Increment the type count
            if j_type not in type_counter:
                type_counter[j_type] = 1
            else:
                type_counter[j_type] += 1

            # Add the numbered type to i_arr
            numbered_type = f"{j_type}_{type_counter[j_type]}"
            i_arr.append({numbered_type: j})
        
        # Sort the list of dictionaries by their keys alphabetically
        i_arr_sorted = sorted(i_arr, key=lambda d: list(d.keys())[0])
        final_classified_data.append(i_arr_sorted)

    return final_classified_data

if __name__ == '__main__':
    urls = [
        'https://www.cars.com/shopping/results/?stock_type=all&makes%5B%5D=bmw&models%5B%5D=bmw-128&maximum_distance=all&zip=48061',
        'https://www.autotrader.ca/cars/?rcp=0&rcs=0&prx=100&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch&mdl=Accord&make=Honda&loc=N5V%204E1',
        'https://www.edmunds.com/inventory/srp.html?make=honda&model=honda%7Ccivic',
        'https://www.cargurus.ca/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&srpVariation=SEARCH_AS_FILTERS&makeModelTrimPaths=m6%2Fd586&zip=N5Z',
        'https://www.kijiji.ca/b-cars-trucks/peterborough/new__used/c174l1700218a49',
        'https://londonon.craigslist.org/search/cta',
    ]
    for url in urls:
        print("=====================================")
        print("url:", url)
        site_url = url 
        driver = open_site_selenium(site=site_url)
        maximize_the_window(driver)
        soup = get_driver_soup(driver)

        final_classified_data = full_conversion(soup)
        for i in final_classified_data:
            for j in i:
                log_function(log_string=j)
            log_function(log_string="================================================================================")
        close_driver(driver)    
