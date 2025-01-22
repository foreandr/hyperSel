import graph
import log
import csv
import util


def find_most_children_node(G):
    """
    Finds the node with the most children based on the criteria and returns a list of the children's text content.
    Removes nodes where the text is an empty list.
    """
    def count_children(node):
        return G.nodes[node]["child_count"]

    # Remove nodes where text is an empty list
    nodes_to_remove = [node for node in G.nodes if G.nodes[node]["metadata"].get("text") == []]
    G.remove_nodes_from(nodes_to_remove)

    valid_nodes = [
        node for node in G.nodes
        if not G.nodes[node].get("exclude_from_most_children", False)
    ]

    most_children_node = max(valid_nodes, key=count_children)

    # Get all children of the node
    children = list(G.successors(most_children_node))

    # Collect the text content of each child
    children_texts = [G.nodes[child]["metadata"].get("text", []) for child in children]

    return children_texts


def main(soup):
    """
    Main function to build the graph and visualize it interactively.
    """
    G = graph.soup_to_graph(soup)

    # Use Pyvis interactive visualization
    # graph.visualize_graph_pyvis(graph)

    children_texts = find_most_children_node(G)
    data = data_preprocessing(data=children_texts)
    file = "./logs/temp_data2.csv"
    util.write_to_csv(data, filename=file)

    # Example: Load the data back
    loaded_data = util.read_from_csv(file)
    print(loaded_data)

def data_preprocessing(data, root_url=None):
    """
    Preprocesses the extracted data by:
    - Removing unwanted symbols and characters.
    - Adding the root URL to relevant items if they are relative URLs.
    """
    
    
    # Create a comprehensive list of unwanted symbols
    unwanted_symbols = set(util.valid_html_tags + util.things_to_add_in_multiple_of_n)
    
    processed_data = []
    for row in data:
        clean_row = []
        for item in row:
            # Skip unwanted symbols
            if item in unwanted_symbols or all(char in unwanted_symbols for char in item):
                continue
            # Add root URL to relative URLs
            if item.startswith("/"):
                item = f"{str(root_url)}{item}"
            clean_row.append(item)
        if clean_row:
            processed_data.append(clean_row)
    
    return processed_data

if __name__ == "__main__":
    import instance
    browser = instance.Browser(
        driver_choice="selenium", 
        headless=False, 
        use_tor=False,
        default_profile=False
    )  

    # 
    browser.go_to_site("https://londonon.craigslist.org/search/cta#search=1~gallery~0~0") 
    soup = browser.return_current_soup()

    # soup = log.load_file_as_soup(file_path="./logs/2025/01/21/2025-01-21.txt")
    main(soup)
