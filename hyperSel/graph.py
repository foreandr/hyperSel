import networkx as nx
from bs4 import BeautifulSoup
from pyvis.network import Network
from datetime import datetime
import log
import parser2

def soup_to_graph(soup):
    """
    Converts a Beautiful Soup object into a NetworkX graph.
    Extracts URLs and image sources, skipping certain metadata tags.
    """
    skippers = [
        'class', 'data-testid', 'height', 'width', 'aria-hidden',
        'style', 'loading', 'id', "viewbox", "aria-pressed", "aria-label", "role",
        'lang', "type"
    ]

    exclude_heads = ["body", "head"]
    exclude_children = ["link", "a"]

    G = nx.DiGraph()

    def build_graph(node, parent=None):
        if node.name:  # Process HTML tags
            
            # Extract metadata, excluding skippers
            metadata = {k: v for k, v in node.attrs.items() if k not in skippers}
            
            # Add tag name
            metadata["tag"] = node.name
            
            # Add text content
            metadata["text"] = list(node.stripped_strings)
            
            # Extract specific attributes like src and href
            if "src" in node.attrs:
                metadata["src"] = node["src"]  # Image sources
                # print('node["src"]', node["src"])

            if "href" in node.attrs:
                metadata["href"] = node["href"]  # Hyperlinks

            # Use a simplified node ID
            tag_id = f"node_{id(node)}"
            #if "1960 GMC suburban" in str(metadata):
            #    print(f"Node {tag_id} Metadata: {metadata}")
            #    input("---")

            G.add_node(tag_id)
            G.nodes[tag_id]["metadata"] = metadata  # Store metadata directly

            # Add edge from parent to this node
            if parent:
                G.add_edge(parent, tag_id, relationship="child")

            # Process child nodes recursively
            for child in node.children:
                build_graph(child, tag_id)

        elif isinstance(node, str) and node.strip():  # Process text content
            # Add text content as a separate node
            text_id = f"text_{id(node)}"
            G.add_node(text_id)
            G.nodes[text_id]["metadata"] = {
                "tag": "text",
                "text": [node.strip()],
            }
            if parent:
                G.add_edge(parent, text_id, relationship="text")

    build_graph(soup)

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

def visualize_graph_pyvis(graph):
    """
    Visualizes the given NetworkX graph as an interactive tree using Pyvis.
    Highlights the node with the most children in red.
    """
    net = Network(notebook=False, height="800px", width="100%", directed=True)

    # Identify the node with the most children
    most_children_node, _ = parser2.find_most_children_node(graph)

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
    html_file = "graph.html"
    net.write_html(html_file)

    add_custom_section(html_file)


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
