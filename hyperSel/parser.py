import networkx as nx
import unicodedata
import log
import util
import classifier
import config
import math
import statistics
from tabulate import tabulate

def normalize_label(label):
    """Normalize node labels to ASCII and replace unsupported characters."""
    return ''.join(
        c if ord(c) < 128 else '?' for c in unicodedata.normalize('NFKD', label)
    )

def extract_all_attributes(tag):
    
    """Extract all attributes, text, URLs, and individual text sections from a tag."""
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

        # Debug condition for specific content

    # Extract all individual texts in the tag using stripped_strings
    individual_texts = list(tag.stripped_strings)
    if "2015 Honda" in individual_texts and "Civic EX" in individual_texts:
        # print(individual_texts)
        for i,item in enumerate(individual_texts):
            print(i, item)
        log.log_function(log_string=f"tag: {tag}", file_name=file, verbose=True)
        input("PRINT INDIVIUDAL TEXTS")
    # print("Extracted individual_texts:", individual_texts)
    # log.log_function(log_string=f"{individual_texts}", file_name=file)
    
    # input("--")
    for i in individual_texts:
        if type(i) != str:
            input("NOT STR", i)
        # print(type(i), i)
        sections.append(i)

    attributes['partitioned_text'] = sections  # Store partitioned text as a list

    log.log_function(log_string=f"attributes: {attributes}", file_name=file, verbose=True)

    urls = []
    for key, value in tag.attrs.items():
        if key in ["href", "src", "data-url"] and isinstance(value, str):
            urls.append(value)
    if urls:
        attributes['urls'] = urls

    return attributes

def html_to_graph(soup):
    log.checkpoint()
    skippers = [
        'class', 'data-testid', 'height', 'width', 'aria-hidden',
        'style', 'loading', 'id', "viewbox", "aria-pressed", "aria-label", "role",
        'lang', "type"
    ]
    """Convert a BeautifulSoup object into a NetworkX directed graph."""
    graph = nx.DiGraph()

    # Recursive function to add nodes and edges
    def add_nodes_edges(tag, parent=None):
        try:
            if tag.name:
                label = normalize_label(tag.name)
                attributes = extract_all_attributes(tag)
                main_string = f"{type(attributes)} | {attributes}"
                # log.log_function(log_string=f"{main_string}", file_name="testerino", verbose=True)

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

                #for key,value in attribute_dict.items():
                #    main_string = f"{type(value)} | {key}:{value}"
                    # log.log_function(log_string=f"{i}:{main_string}", file_name=file, verbose=True)
                #    log.log_function(log_string=f"{main_string}", file_name=file, verbose=True, new_line=True)
                    #print("key  :", key)
                    #print("value:", value)

        except Exception as e:
            print(f"[Error] {e}")
            print(tag)
            # input("---")

    add_nodes_edges(soup)
    # exit()
    return graph

def extract_relevant_data_flat(descendants):
    log.checkpoint()
    wanted_tags = ["label", "class", "href", "src", "text", "urls", "alt", "title", "data-pid", "value", "partitioned_text"]
    """
    Extract and flatten meaningful data from descendants into a list.
    """
    flattened_data = []

    for i, descendant in enumerate(descendants):
        print("DESCENDENT", i, descendant)

        label = descendant.get("label", "")
        if label == "button":
            if config.VERBOSE_DEBUG_FLAG:
                print("NOTE, WE ARE SKIPPING BUTTONS HERE BECAUSE MOST UI ARE NOT GUNNA HAVE USEFUL INFO IN THERE")
            continue

        # Include all meaningful attributes
        if label:
            filtered_descendant = {}
            for k, v in descendant.items():
                if k in wanted_tags:
                    # print("k:", k, "v:", v)
                    filtered_descendant[k] = v
            flattened_data.append(filtered_descendant)

    return flattened_data

def filter_valid_nodes(graph):
    excluded_labels = ['select', 'body', 'head', 'svg', 'html', "a"]
    log.checkpoint()

    """Filter out nodes with labels in excluded_labels."""
    valid_nodes = []
    for node in graph.nodes:
        label = graph.nodes[node].get('label', 'Unknown')
        if label not in excluded_labels:
            valid_nodes.append(node)
        # else:
    return valid_nodes

def get_children(graph, node):
    """
    Retrieve children for a given node, excluding nodes with specific labels or tags.
    """
    # Define a list of excluded labels and tags
    excluded_labels = ['script', 'a']

    # Initialize an empty list for valid children
    children = []

    # Iterate through the successors of the given node
    for child in graph.successors(node):
        # Retrieve label and tag for debugging
        label = graph.nodes[child].get('label', 'Unknown')

        # Print the label and tag for debugging
        # print(f"Child: {child}, Label: {label}")

        # Exclude nodes with specified labels or tags
        if label in excluded_labels:
            continue

        # Add the valid child to the list
        children.append(child)

    return children


def calculate_child_data_lengths(graph, children):
    """Calculate string data lengths for all children of a node."""
    data_lengths = []
    for child in children:
        attributes = graph.nodes[child]
        child_data_length = sum(
            len(value) if isinstance(value, str) else sum(len(str(v)) for v in value)
            for key, value in attributes.items() if isinstance(value, (str, list))
        )
        data_lengths.append(child_data_length)
        # Debug: Print each child's attributes and data length
        # print(f"  Child: {child}, Attributes: {attributes}, Data Length: {child_data_length}")
    return data_lengths


def calculate_stats(data_lengths):
    """Calculate detailed statistics for the given data."""
    total_data_length = sum(data_lengths)
    avg_chars = total_data_length / len(data_lengths)
    variance = sum((x - avg_chars) ** 2 for x in data_lengths) / len(data_lengths)
    std_dev = math.sqrt(variance)
    relative_spread = std_dev / avg_chars if avg_chars > 0 else 0
    
    # Additional statistics
    median = statistics.median(data_lengths)
    mode = statistics.mode(data_lengths) if len(set(data_lengths)) > 1 else "No mode"
    data_range = max(data_lengths) - min(data_lengths)
    
    return {
        'avg_chars': avg_chars,
        'std_dev': std_dev,
        'relative_spread': relative_spread,
        'median': median,
        'mode': mode,
        'range': data_range
    }


def filter_nodes_by_constraints(node, children, avg_chars):
    """Check if a node meets the constraints."""
    if (
        config.MIN_CHILDREN <= len(children) <= config.MAX_CHILDREN
        and avg_chars >= config.AVG_CHARS_MINIMUM
    ):
        return True
    # print(f"Node: {node} does not meet constraints.")  # Debug
    return False


def find_most_consistent_node(consistency_data):
    """Find the node with the lowest relative spread."""
    if not consistency_data:
        # print("No nodes met the consistency criteria.")  # Debug
        return None
    return min(consistency_data, key=lambda x: x['relative_spread'])


def print_node_data(graph, node):
    """
    Print the data of a node and its children in a readable format.
    """
    print(f"\nNode: {node}")
    node_data = graph.nodes[node]
    print("Node Metadata:")
    for key, value in node_data.items():
        print(f"{key}: {value}")

    children = get_children(graph, node)

    print("  Children:")
    for child in children:
        child_data = graph.nodes[child]
        print(f"    - Child: {child}")
        for key, value in child_data.items():
            print(f"        {key}: {value}")
            print("-")
        print("====")

    
def calculate_children_count(graph):
    log.checkpoint()
    """
    Calculate the number of children for each node, excluding certain labels,
    and remove nodes with fewer than a configured range of children.
    Additionally, calculate detailed statistics and output a well-formatted table,
    including node properties retrieved from the graph.
    """
    valid_nodes = filter_valid_nodes(graph)
    consistency_data = []
    
    print("\n\n*****************************************************************")
    print("num_valid nodes:", len(valid_nodes))

    for i, node in enumerate(valid_nodes):
        # Get and log main node properties
        node_properties = graph.nodes[node]
        main_string = f"Main Node: {node}, Properties: {node_properties}"
        # log.log_function(log_string=f"{i}:{main_string}", file_name=file, verbose=True)

        children = get_children(graph, node)
        if len(children) < config.MIN_CHILDREN:
            continue
        print(len(children))

        # Log children properties
        children_strings = []
        for child in children:
            child_properties = graph.nodes[child]
            child_string = f"Child Node: {child}, Properties: {child_properties}"
            # print(child_string)
            children_strings.append(child_string)


        data_lengths = calculate_child_data_lengths(graph, children)

        if not data_lengths:
            print("NO LENGTHS?", stats['avg_chars'], "  |    NUM CHILD:", len(children))
            continue

        stats = calculate_stats(data_lengths)

        # Skip nodes with insufficient avg_chars
        if stats['avg_chars'] < config.AVG_CHARS_MINIMUM:
            print("TOO LOW AVG CHARS", stats['avg_chars'], "  |    NUM CHILD:", len(children))
            continue

        # Retrieve node properties from the graph for the output
        node_summary = {
            'id': node,
        }

        # Add only nodes passing all filters to consistency_data
        consistency_data.append({
            'node': node_summary,
            'children_count': len(children),
            **stats
        })

    print_tabulated_data(consistency_data)
    most_consistent = find_most_consistent_node(consistency_data)

    # input("-------")

    # Print the most consistent node details
    print("most_consistent['node']['id']:", most_consistent)
    input("--")

    if not consistency_data:
        return []
    
    if most_consistent:
        # print_node_data(graph, most_consistent['node'])
        return most_consistent['node']['id']
    
    print("we hit the failure mode?")
    input("--")
    return []

def print_tabulated_data(consistency_data): 
    # Create table headers and rows
    headers = [
        "Node", "Children Count", "Std Dev",
        "Relative Spread", "Avg Chars", "Median", "Mode", "Range"
    ]
    rows = [
        [
            entry['node'], 
            entry['children_count'], 
            f"{entry['std_dev']:.2f}", 
            f"{entry['relative_spread']:.2f}",
            f"{entry['avg_chars']:.2f}",
            f"{entry['median']:.2f}", 
            f"{entry['mode']:.2f}", 
            f"{entry['range']:.2f}", 
        
        ]
        for entry in consistency_data
    ]

    print(tabulate(rows, headers, tablefmt="grid"))

def search_graph_for_string(graph, search_string):
    """
    Search the entire graph for a specific string in node attributes.
    Outputs the node and the string where the search string is found.
    """
    matches = []

    for node, attributes in graph.nodes(data=True):
        for key, value in attributes.items():
            if isinstance(value, str) and search_string in value:
                matches.append((node, value))  # Add the node and matching string
            elif isinstance(value, (list, dict)):  # Handle complex structures
                if search_string in str(value):
                    matches.append((node, str(value)))

    # Output matching nodes and strings
    for match in matches:
        if len(match[1]) <30:
            print(match[1])
        print(f"Node: {match[0]} | Containing String: {len(match[1])}")

    return matches


def collect_child_details(graph, top_node):
    log.checkpoint()
    print("graph   :", graph)
    print("top_node1:", top_node)
    """
    Collect details about the children of the top node.
    """
    children_details = []

    def gather_all_data_recursive(node, combined_data):
        """
        Recursively gather all data for the node and its descendants.
        """
        # Add the node's attributes to the combined data
        node_attrs = graph.nodes[node]
        for key, value in node_attrs.items():
            if key in combined_data:
                counter = 1
                new_key = f"{key}{counter}"
                while new_key in combined_data:
                    counter += 1
                    new_key = f"{key}{counter}"
                combined_data[new_key] = value
            else:
                combined_data[key] = value

        # Recur for all children of this node
        for child in graph.successors(node):
            gather_all_data_recursive(child, combined_data)

    for child in graph.successors(top_node):
        print("top_node2:", top_node)
        #print("\n\n\nchild:", child)

        # Initialize combined_data for this child
        combined_data = {}

        # Gather all data recursively down to the root for this child
        gather_all_data_recursive(child, combined_data)
        #print("Combined Data Before Processing:", combined_data)

        # Ensure `sort_unique_descendants` receives a list
        unique_descendants = sort_unique_descendants([combined_data])

        # Flatten meaningful data
        relevant_flattened = extract_relevant_data_flat(unique_descendants)

        #print("FLATTENED DATA:", type(relevant_flattened), len(relevant_flattened))
        #for i in relevant_flattened:
        #    print(i)
        #    print("===")

        # Add the processed child details to the result
        children_details.append({
            "label": graph.nodes[child].get('label', 'Unknown'),
            "attributes": graph.nodes[child],
            "flattened_relevant_data": relevant_flattened
        })
        # print("**********************************************************************")

    # # input("--")

    #for i in children_details:
    #    print(i)
    #    print("--")

    return children_details


def sort_unique_descendants(descendant_attributes):
    log.checkpoint()
    
    """
    Sort and deduplicate descendant attributes for a node.
    """
    unique_items = {}

    for item in descendant_attributes:
        # print("item:", item)
        if isinstance(item, dict):
            normalized_item = []
            for k, v in item.items():
                if isinstance(v, list):
                    v = tuple(v)  # Convert lists to tuples for immutability
                normalized_item.append((k, v))
            normalized_item = tuple(sorted(normalized_item))  # Sort for consistent deduplication
            unique_items[normalized_item] = item

    sorted_items = sorted(unique_items.values(), key=lambda x: x.get('label', 'Unknown'))

    #for i in sorted_items:
    #    print(i)
    

    return sorted_items

def find_top_node_with_most_children(graph):
    log.checkpoint()
    """
    Main function to find the top node with the most children.
    """
    

    top_node = calculate_children_count(graph)
    print("top_node3:", top_node)
    # exit()

    children_details = collect_child_details(graph, top_node)
    # print("children_details:", children_details)

    attributes = graph.nodes[top_node]
    # # exit()

    #for key,value in attributes.items():
    #    print("key  :", key)
    #    print("value:", value)
    #    print("----")
    # # exit()

    #print("children_details:", type(children_details))
    #for i in children_details:
    #    for key, value in i.items():
    #        print(key, value)
    #    print("================================")

    return {
        "children": children_details,
    }

def process_soup(soup):
    log.checkpoint()
    """Main function to process a BeautifulSoup object and return analysis."""
    # print("[process_soup] Processing soup into graph.")
    graph = html_to_graph(soup)
    # search_graph_for_string(graph, search_string="2015 Honda")
    node_with_most_children = find_top_node_with_most_children(graph)

    return node_with_most_children

def process_results(result):
    """Process and print the results from the top node analysis."""
    if not result:
        # print("No valid nodes found in the graph.")
        return
    
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
    
    # print("data:", len(data))

    flattended_data = remove_larger_strings(data, length_threshold=100)
    # print(" flattended_data", len( flattended_data))

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
    import instance
    browser = instance.Browser(
        driver_choice="selenium", 
        headless=False, 
        use_tor=False,
        default_profile=False
    )  

    # 
    browser.go_to_site("https://www.carmax.com/cars?search=honda+civic") 
    soup = browser.return_current_soup()
    log.log_function(soup)
    exit()
    # soup = log.load_file_as_soup("./logs/2025/01/19/2025-01-19.txt")
    file = "testerino"
    final_classified_data = full_conversion(soup)

    iteration = 1
    for i in final_classified_data:
        for j in i:
            log.log_function(log_string=f"{iteration}:{j}", file_name=file)
        log.log_function(log_string="================================================================================", file_name=file)
        iteration+=1
        # # input("----")
    # input("--")
    print("I GOT TO THE END??")
