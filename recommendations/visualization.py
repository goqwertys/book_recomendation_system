import json
from pathlib import Path
from pyvis.network import Network

BASE_DIR = Path(__file__).resolve().parent.parent
VIS_ROOT = BASE_DIR / 'recommendations' / 'visualizations'


def ensure_paths():
    """Creates the necessary directories"""
    (VIS_ROOT / 'saved_graphs').mkdir(parents=True, exist_ok=True)
    (VIS_ROOT / 'config').mkdir(parents=True, exist_ok=True)


def load_config():
    """Loads the visualization configuration"""
    config_path = VIS_ROOT / 'config' / 'graph_config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}. Using default settings.")
        return {
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "levelSeparation": 250
                }
            }
        }


def visualize_interactive_graph(G, output_file='graph.html'):
    """Visualizes a graph with data validation and encoding"""
    ensure_paths()
    config = load_config()

    # Check for empty graph
    if len(G.nodes) == 0:
        print("Error: The graph does not contain nodes. Check the input data.")
        return

    net = Network(
        notebook=False,
        height='900px',
        width='100%',
        bgcolor='#ffffff',
        font_color='black',
        cdn_resources='in_line'
    )

    try:
        net.from_nx(G)
        net.set_options(json.dumps(config))

        output_path = VIS_ROOT / 'saved_graphs' / output_file

        # Explicitly specifying UTF-8 encoding
        html = net.generate_html()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f'The graph is saved: {output_path.relative_to(BASE_DIR)}')
        print(f'Nodes: {len(G.nodes)}, Connections: {len(G.edges)}')

    except Exception as e:
        print(f"Visualization error: {str(e)}")
