import networkx as nx
from pyvis.network import Network
from datetime import datetime

try:
    from . import parser
except:
    import parser as parser

def initialize_graph():
    """
    Initializes a directed graph using NetworkX.
    """
    return nx.DiGraph()

def process_html_node(node, skippers):
    """
    Processes a single HTML node to extract metadata, removing duplicates.
    """
    metadata = {}

    # Filter attributes, excluding those in skippers
    for k, v in node.attrs.items():
        if k not in skippers:
            metadata[k] = v

    # Add tag name
    metadata["tag"] = node.name

    # Add text content (remove duplicates while preserving order)
    seen_text = set()
    metadata["text"] = []
    for string in node.stripped_strings:
        if string not in seen_text:
            metadata["text"].append(string)
            seen_text.add(string)

    # Search for 'href' and 'src' in all descendant nodes, removing duplicates
    metadata["href"] = list(set(a["href"] for a in node.find_all("a", href=True)))
    metadata["src"] = list(set(img["src"] for img in node.find_all("img", src=True)))

    # Remove empty lists if no links or images exist
    if not metadata["href"]:
        del metadata["href"]
    if not metadata["src"]:
        del metadata["src"]

    return metadata


def add_node_to_graph(G, node_id, metadata, parent=None):
    """
    Adds a node and its metadata to the graph. Creates an edge to the parent if provided.
    """
    G.add_node(node_id)
    G.nodes[node_id]["metadata"] = metadata
    
    if parent:
        G.add_edge(parent, node_id, relationship="child")


def traverse_and_build_graph(node, parent, G, skippers):
    # print("NOTE IF THERE IS DATA MISSING, IT IS PROBABLY THIS FUNCTION")

    """
    Recursively traverses the HTML tree and builds the graph.
    """
    if node.name:  # Process HTML tags
        metadata = process_html_node(node, skippers)
        node_id = f"node_{id(node)}"
        add_node_to_graph(G, node_id, metadata, parent)

        for child in node.children:
            traverse_and_build_graph(child, node_id, G, skippers)

    elif isinstance(node, str) and node.strip():  # Process text content

        #print("\n\n========================================")
        #print("node:", node)
        #input("--")

        text_id = f"text_{id(node)}"
        G.add_node(text_id)
        G.nodes[text_id]["metadata"] = {
            "tag": "text",
            "text": [node.strip()],
        }
        if parent:
            G.add_edge(parent, text_id, relationship="text")


def finalize_graph(G, exclude_children, exclude_heads):
    """
    Finalizes the graph by relabeling nodes and adding computed properties.
    """
    # Map nodes to compatible IDs for visualization
    mapping = {n: f"node_{i}" for i, n in enumerate(G.nodes())}
    G = nx.relabel_nodes(G, mapping)

    # Calculate child counts for each node
    for node in G.nodes:
        G.nodes[node]["child_count"] = sum(
            1 for child in G.successors(node)
            if G.nodes[child]["metadata"].get("tag") not in exclude_children
        )

    # Exclude specific heads
    for node in G.nodes:
        G.nodes[node]["exclude_from_most_children"] = G.nodes[node]["metadata"].get("tag") in exclude_heads

    return G


def soup_to_graph(soup):
    """
    Converts a Beautiful Soup object into a NetworkX graph.
    """
    skippers = [
        'class', 'data-testid', 'height', 'width', 'aria-hidden',
        'style', 'loading', 'id', "viewbox", "aria-pressed", "aria-label", "role",
        'lang', "type"
    ]

    exclude_heads = ["body", "head"]
    exclude_children = ["link", "a"]

    # Step 1: Initialize the graph
    G = initialize_graph()

    # Step 2: Build the graph recursively
    traverse_and_build_graph(soup, parent=None, G=G, skippers=skippers)

    # Step 3: Finalize the graph
    G = finalize_graph(G, exclude_children=exclude_children, exclude_heads=exclude_heads)

    return G

def visualize_graph_pyvis(graph):
    """
    Visualizes the given NetworkX graph as an interactive tree using Pyvis.
    Highlights the node with the most children in red.
    """
    net = Network(notebook=False, height="800px", width="100%", directed=True)

    # Identify the node with the most children
    most_children_node, _ = parser.find_most_children_node(graph)

    # Add nodes and edges from the NetworkX graph
    for node, data in graph.nodes(data=True):
        metadata = data.get("metadata", {})
        tooltip = "<br>".join(f"{key}: {value}" for key, value in metadata.items())
        label = metadata.get("tag", "")
        color = "red" if node == most_children_node else "#97C2FC"  # Highlight most children node in red

        net.add_node(
            node,
            label=label,
            shape="dot",
            size=15,
            title=tooltip,
            color=color,
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
    html_file = "site_graph.html"
    net.write_html(html_file)

    add_custom_section(html_file)
    print("VISUALIZED GRAPH")


def add_custom_section(html_file):
    """
    Adds a custom header or footer section to the generated HTML file.
    """
    custom_text = f"""
    <div style="text-align: center; margin-top: 20px; font-family: Arial, sans-serif;">
        <h2>Graph Visualization</h2>
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
