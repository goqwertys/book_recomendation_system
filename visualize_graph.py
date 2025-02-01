import argparse
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recommendations.graph_builder import build_filtered_graph
from recommendations.visualization import visualize_interactive_graph


def main():
    parser = argparse.ArgumentParser(description="Visualize user-book interactions graph")
    parser.add_argument(
        "--max_users",
        type=int,
        default=30,
        help="Maximum number of users to include (default: 30)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="graph.html",
        help="Output filename (will be saved in recommendations/visualizations/saved_graphs/)"
    )

    args = parser.parse_args()

    G = build_filtered_graph(max_users=args.max_users)
    visualize_interactive_graph(G, args.output)


if __name__ == "__main__":
    main()
