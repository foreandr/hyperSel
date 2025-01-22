import networkx as nx
from bs4 import BeautifulSoup
from pyvis.network import Network
from datetime import datetime
import log

def soup_to_graph(soup):
    """
    Converts a Beautiful Soup object into a NetworkX graph.
    Skips certain metadata tags defined in the skippers list.
    Includes all nodes in the graph but excludes specific heads and children tags from counts.
    """
    skippers = [
        'class', 'data-testid', 'height', 'width', 'aria-hidden',
        'style', 'loading', 'id', "viewbox", "aria-pressed", "aria-label", "role",
        'lang', "type"
    ]

    exclude_heads = ["body", "head"]  # Nodes to include in the graph but exclude from being the "most children" candidate
    exclude_children = ["link", "a"]  # Tags to exclude from child counts

    # Initialize the graph
    G = nx.DiGraph()

    # Recursive function to traverse the DOM
    def build_graph(node, parent=None):
        if node.name:  # Process HTML tags
            # Extract metadata, excluding skippers
            metadata = {k: v for k, v in node.attrs.items() if k not in skippers}
            metadata["tag"] = node.name  # Add the tag name
            metadata["text"] = node.get_text(strip=True)  # Add text content

            # Use a simplified node ID
            tag_id = f"node_{id(node)}"
            G.add_node(tag_id)  # Add the node with a simple ID
            G.nodes[tag_id]["metadata"] = metadata  # Store metadata in a single attribute

            # Add edge from parent to this node
            if parent:
                G.add_edge(parent, tag_id, relationship="child")

            # Process child nodes recursively
            for child in node.children:
                build_graph(child, tag_id)

        elif isinstance(node, str) and node.strip():  # Process text content
            # Add text content as a separate node
            text_id = f"text_{id(node)}"
            G.add_node(text_id)  # Add a simple node
            G.nodes[text_id]["metadata"] = {"tag": "text", "text": node.strip()}  # Store metadata
            if parent:
                G.add_edge(parent, text_id, relationship="text")

    # Start from the root of the soup
    build_graph(soup)

    # Ensure node IDs are compatible with pydot
    mapping = {n: f"node_{i}" for i, n in enumerate(G.nodes())}
    G = nx.relabel_nodes(G, mapping)

    # Calculate child counts excluding specific children
    for node in G.nodes:
        G.nodes[node]["child_count"] = sum(
            1 for child in G.successors(node)
            if G.nodes[child]["metadata"].get("tag") not in exclude_children
        )

    # Mark excluded heads so they are not considered for "most children"
    for node in G.nodes:
        if G.nodes[node]["metadata"].get("tag") in exclude_heads:
            G.nodes[node]["exclude_from_most_children"] = True
        else:
            G.nodes[node]["exclude_from_most_children"] = False

    return G

def visualize_graph_pyvis(graph):
    """
    Visualizes the given NetworkX graph as an interactive tree using Pyvis.
    Ensures the tree structure by enforcing a hierarchical layout and adds custom text.
    """
    net = Network(notebook=False, height="800px", width="100%", directed=True)

    # Find the node with the most children, excluding specified heads
    def count_children(node):
        return graph.nodes[node]["child_count"]

    valid_nodes = [
        node for node in graph.nodes
        if not graph.nodes[node].get("exclude_from_most_children", False)
    ]

    most_children_node = max(valid_nodes, key=count_children)

    # Add nodes and edges from the NetworkX graph
    for node, data in graph.nodes(data=True):
        # Prepare metadata for tooltip
        metadata = data["metadata"]
        tooltip = "<br>".join(f"{key}: {value}" for key, value in metadata.items())

        # Highlight the node with the most children in red
        color = "red" if node == most_children_node else "#97C2FC"

        # Add node with metadata in the tooltip
        net.add_node(
            node,
            label=metadata.get("tag", ""),  # Show only the tag in the graph
            shape="dot",
            size=20,
            title=tooltip,  # Tooltip displays full metadata
            color=color  # Set color based on highlight condition
        )

    for edge in graph.edges():
        net.add_edge(edge[0], edge[1])

    # Force hierarchical layout (tree)
    net.set_options("""
    {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed"
        }
      },
      "physics": {
        "enabled": false
      }
    }
    """)

    # Save the HTML file
    html_file = "graph.html"
    net.write_html(html_file)

    # Add custom content to the HTML
    add_custom_section(html_file)

def add_custom_section(html_file):
    """
    Adds a custom header or footer section to the generated HTML file.
    """
    custom_text = f"""
    <div style="text-align: center; margin-top: 20px; font-family: Arial, sans-serif;">
        <h2>Graph Visualization</h2>
        <p>Generated by: Your Name</p>
        <p>Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    """

    # Read the existing HTML
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Insert custom text just before the closing </body> tag
    updated_content = html_content.replace("</body>", f"{custom_text}\n</body>")

    # Write the updated HTML back to the file
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(updated_content)

def main(soup):
    """
    Main function to build the graph and visualize it interactively.
    """
    graph = soup_to_graph(soup)

    # Use Pyvis interactive visualization
    visualize_graph_pyvis(graph)

if __name__ == "__main__":
    # Parse the HTML content using BeautifulSoup
    #import util  # Ensure `util.html` contains your HTML
    #soup = BeautifulSoup(util.html, "html.parser")
    soup = log.load_file_as_soup(file_path="./logs/2025/01/21/2025-01-21.txt")
    main(soup)
