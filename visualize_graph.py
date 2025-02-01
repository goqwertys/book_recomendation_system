import argparse
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recommendations.graph_builder import build_filtered_graph
from recommendations.visualization import visualize_interactive_graph


def main():
    parser = argparse.ArgumentParser(
        description="Visualize user-book interactions graph",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # Shows default values
    )

    # Basic filtering parameters
    parser.add_argument(
        "--max_users",
        type=int,
        default=30,
        help="Maximum number of most active users to include (default: %(default)s)"
    )
    parser.add_argument(
        "--max_books",
        type=int,
        default=50,
        help="Maximum number of most popular books to include (default: %(default)s)"
    )
    parser.add_argument(
        "--min_interactions",
        type=int,
        default=1,
        dest="min_book_interactions",
        help="Minimum interactions required to include a book (default: %(default)s)"
    )

    # Output options
    parser.add_argument(
        "--output",
        type=str,
        default="graph.html",
        help="Output filename (saved to recommendations/visualizations/saved_graphs/)"
    )

    args = parser.parse_args()

    # We pass all parameters to the graph construction function
    G = build_filtered_graph(
        max_users=args.max_users,
        max_books=args.max_books,
        min_book_interactions=args.min_book_interactions
    )

    visualize_interactive_graph(G, args.output)


if __name__ == "__main__":
    main()
