import os
import django
import networkx as nx
import matplotlib.pyplot as plt
import argparse
from matplotlib.colors import LinearSegmentedColormap

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from books.models import Book
from interactions.models import Interaction
from recommendations.algorithms.collaborative import user_based_collaborative_filtering
from recommendations.algorithms.k_nearest_neighbors import find_k_nearest_neighbors
from users.models import User


def build_filtered_graph(users, books, interactions):
    G = nx.Graph()

    # Users
    for user in users:
        G.add_node(user.id, label=str(user.id), type="user", color="lightgray")

    # Books
    for book in books:
        G.add_node(book.id, label=book.title, type="book", color="lightgray")

    # Interactions
    for interaction in interactions:
        if interaction.user_id in G and interaction.book_id in G:
            G.add_edge(interaction.user_id, interaction.book_id, weight=interaction.rating or 1.0, color="gray")

    return G


def apply_pagerank(G, user_id):
    pagerank_scores = nx.pagerank(G, weight='weight')

    # Normalizing scores only for books
    book_scores = {node: score for node, score in pagerank_scores.items() if G.nodes[node]["type"] == "book"}
    if not book_scores:
        return

    min_score = min(book_scores.values())
    max_score = max(book_scores.values())

    # Colorize books and their edges
    cmap = LinearSegmentedColormap.from_list("book_cmap", ["lightgreen", "darkgreen"])
    for node, score in book_scores.items():
        if G.nodes[node].get("color") == "lightgray":  # Colorizing if the color has not been changed by another algorithm.
            normalized_score = (score - min_score) / (max_score - min_score)
            G.nodes[node]["color"] = cmap(normalized_score)
            for neighbor in G.neighbors(node):
                if G.edges[node, neighbor].get("color") == "gray":  # Colorizing only if the color has not been changed by another algorithm.
                    G.edges[node, neighbor]["color"] = cmap(normalized_score)

    return book_scores


def visualize_graph(G, output_file, dpi=100, edge_width_factor=5.0):
    # Nodes
    users = [node for node, attrs in G.nodes(data=True) if attrs["type"] == "user"]
    books = [node for node, attrs in G.nodes(data=True) if attrs["type"] == "book"]

    # Pos
    pos = {}
    user_spacing = 1.0 / (len(users) + 1)
    book_spacing = 1.0 / (len(books) + 1)

    # Users
    for i, user in enumerate(users):
        pos[user] = (0, (i + 1) * user_spacing)

    # Books
    for i, book in enumerate(books):
        pos[book] = (1, (i + 1) * book_spacing)

    # Node colours
    node_colors = [G.nodes[node].get("color", "lightgray") for node in G.nodes]

    # Edge weight and color
    edge_weights = [G.edges[edge].get("weight", 1.0) for edge in G.edges]
    edge_colors = [G.edges[edge].get("color", "gray") for edge in G.edges]

    # Normalizing edge weights
    min_weight = min(edge_weights)
    max_weight = max(edge_weights)
    edge_widths = [edge_width_factor * (weight - min_weight) / (max_weight - min_weight) for weight in edge_weights]

    # Draw graph
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=8, font_color="black")

    # Draw edges
    for edge, width, color in zip(G.edges, edge_widths, edge_colors):
        nx.draw_networkx_edges(G, pos, edgelist=[edge], width=width, edge_color=color, alpha=0.6)

    # Save file with DPI
    plt.savefig(output_file, bbox_inches="tight", dpi=dpi)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default="graph.png")
    parser.add_argument("--pagerank", action="store_true")
    parser.add_argument("--knn", action="store_true")
    parser.add_argument("--cf", action="store_true")
    parser.add_argument("--user_id", type=int, required=True)
    parser.add_argument("--dpi", type=int, default=100, help="Разрешение изображения (DPI)")
    parser.add_argument("--w_factor", type=float, default=5.0, help='Edge width factor')

    args = parser.parse_args()

    # Geting all the objects
    users = User.objects.all()
    books = Book.objects.all()
    interactions = Interaction.objects.all()

    # Building graph
    G = build_filtered_graph(users, books, interactions)

    # Apply algorithms
    if args.pagerank:
        apply_pagerank(G, args.user_id)

    if args.knn:
        knn_users = find_k_nearest_neighbors(args.user_id)
        for user in knn_users:
            if user.id in G:
                G.nodes[user.id]["color"] = "blue"
                for neighbor in G.neighbors(user.id):
                    G.edges[user.id, neighbor]["color"] = "blue"

    if args.cf:
        cf_books = user_based_collaborative_filtering(args.user_id)
        for rec in cf_books:
            if rec["book"].id in G:
                G.nodes[rec["book"].id]["color"] = "blue"
                for neighbor in G.neighbors(rec["book"].id):
                    G.edges[rec["book"].id, neighbor]["color"] = "blue"

    # Highlight user
    if args.user_id in G:
        G.nodes[args.user_id]["color"] = "red"
        for neighbor in G.neighbors(args.user_id):
            G.edges[args.user_id, neighbor]["color"] = "red"

    # Render DPI
    visualize_graph(G, args.output, dpi=args.dpi, edge_width_factor=args.w_factor)


if __name__ == "__main__":
    main()
