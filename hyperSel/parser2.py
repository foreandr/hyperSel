import graph
import log
import csv
import util
from collections import deque


def find_most_children_node(G):
    """
    Finds the node with the most children and returns the node ID and its children's metadata.
    """
    def count_children(node):
        return G.nodes[node]["child_count"]

    # Remove nodes with empty text
    #nodes_to_remove = [node for node in G.nodes if G.nodes[node]["metadata"].get("text") == []]
    #G.remove_nodes_from(nodes_to_remove)

    # Filter valid nodes for the "most children" computation
    valid_nodes = [
        node for node in G.nodes
        if not G.nodes[node].get("exclude_from_most_children", False)
    ]

    # Find the node with the most children
    most_children_node = max(valid_nodes, key=count_children)

    # Get the children of this node
    children = list(G.successors(most_children_node))

    # Collect metadata for each child
    children_metadata = []
    for child in children:
        # Debugging: print the current child
        # print("Processing child:", G.nodes[child])

        # Initialize a set to collect all unique elements
        flat_metadata = set()

        # Perform a breadth-first traversal
        queue = deque([child])

        while queue:
            current_node = queue.popleft()
            current_metadata = G.nodes[current_node]["metadata"]

            # Add all values from metadata to the set
            for value in current_metadata.values():
                if isinstance(value, list):
                    flat_metadata.update(value)  # Add each item from the list
                elif isinstance(value, str):
                    flat_metadata.add(value)  # Add string values directly

            # Add children of the current node to the queue
            queue.extend(G.successors(current_node))

        # Convert the set to a flat list
        unique_metadata_list = list(flat_metadata)

        # Print the resulting flattened metadata list
        # print("Flattened Metadata:", unique_metadata_list)
        children_metadata.append(unique_metadata_list)
        

    return most_children_node, children_metadata

def main(soup):
    """
    Main function to build the graph and visualize it interactively.
    """
    G = graph.soup_to_graph(soup)

    # Use Pyvis interactive visualization
    graph.visualize_graph_pyvis(G)
    print("GOT HERE")
    # exit()

    most_children_node, children_metadata = find_most_children_node(G)
    

    data = data_preprocessing(data=children_metadata)
    file = "./logs/temp_data2.csv"
    util.write_to_csv(data, filename=file)

    # Example: Load the data back
    loaded_data = util.read_from_csv(file)
    for i in loaded_data:
        print(i)
        print('======================')

def data_preprocessing(data, root_url=None):
    final_data = []

    for i in data:
        # print(i)
        sub_data = []
        for j in i:
            if j in util.valid_html_tags:
                continue
            else:
                sub_data.append(j)
        final_data.append(sub_data)
        # print("---")
    
    #for i in final_data:
    #    print(i)

    return final_data



if __name__ == "__main__":
    '''
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
    
    
    log.log_function(soup)
    exit()
    '''

    soup = log.load_file_as_soup(file_path="./logs/2025/01/21/2025-01-21.txt")
    main(soup)
