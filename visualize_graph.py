import os
import django
import networkx as nx
import matplotlib.pyplot as plt
import json
import argparse
import numpy as np

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # Замени на свой проект
django.setup()

from books.models import Book
from interactions.models import Interaction
from recommendations.algorithms.collaborative import user_based_collaborative_filtering
from recommendations.algorithms.k_nearest_neighbors import find_k_nearest_neighbors
from users.models import User


def load_config():
    with open("graph_config.json", "r") as f:
        return json.load(f)


def build_filtered_graph(users, books, interactions, min_interactions):
    G = nx.Graph()
    config = load_config()

    # Users
    for user in users:
        G.add_node(user.id, label=str(user.id), type="user", color=config.get("user_color", "lightblue"))

    # Books
    for book in books:
        G.add_node(book.id, label=book.title, type="book", color=config.get("default_book_color", "lightgreen"))

    # Interactions
    for interaction in interactions:
        if interaction.user_id in G and interaction.book_id in G:
            G.add_edge(interaction.user_id, interaction.book_id, weight=interaction.rating or 1.0)

    return G


def apply_pagerank(G, user_id):
    pagerank_scores = nx.pagerank(G, weight='weight')

    # Top books
    top_books = sorted(
        [(node, score) for node, score in pagerank_scores.items() if G.nodes[node]["type"] == "book"],
        key=lambda x: x[1],
        reverse=True
    )

    # Top books colours
    for book_id, score in top_books[:10]:
        G.nodes[book_id]["color"] = "orange"
        G.nodes[book_id]["label"] += f"\n({score:.2f})"

    # Highlight user
    if user_id in G:
        G.nodes[user_id]["color"] = "red"

    return top_books


def visualize_graph(G, output_file, dpi=100):
    # Разделяем узлы на пользователей и книги
    users = [node for node, attrs in G.nodes(data=True) if attrs["type"] == "user"]
    books = [node for node, attrs in G.nodes(data=True) if attrs["type"] == "book"]

    # Позиционирование узлов
    pos = {}
    pos.update((node, (1, i)) for i, node in enumerate(users))  # Пользователи слева
    pos.update((node, (2, i)) for i, node in enumerate(books))  # Книги справа

    # Цвета узлов
    node_colors = [G.nodes[node].get("color", "gray") for node in G.nodes]

    # Толщина и цвет рёбер
    edge_weights = [G.edges[edge].get("weight", 1.0) * 0.5 for edge in G.edges]
    edge_colors = [G.edges[edge].get("color", "gray") for edge in G.edges]

    # Нормализация весов для толщины рёбер
    min_weight = min(edge_weights)
    max_weight = max(edge_weights)
    edge_widths = [3 + 5 * (weight - min_weight) / (max_weight - min_weight) for weight in edge_weights]

    # Рисуем граф
    plt.figure(figsize=(30, 20))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=8, font_color="black")

    # Рисуем рёбра с градиентом и толщиной
    for edge, width, color in zip(G.edges, edge_widths, edge_colors):
        nx.draw_networkx_edges(G, pos, edgelist=[edge], width=width, edge_color=color, alpha=0.6)

    # Сохраняем граф в файл с указанным DPI
    plt.savefig(output_file, bbox_inches="tight", dpi=dpi)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_users", type=int, default=100)
    parser.add_argument("--max_books", type=int, default=10)
    parser.add_argument("--min_interactions", type=int, default=10)
    parser.add_argument("--output", type=str, default="graph.png")
    parser.add_argument("--pagerank", action="store_true")
    parser.add_argument("--knn", action="store_true")
    parser.add_argument("--cf", action="store_true")
    parser.add_argument("--user_id", type=int, required=True)
    parser.add_argument("--dpi", type=int, default=100, help="Разрешение изображения (DPI)")  # Новый параметр

    args = parser.parse_args()

    # Получаем всех пользователей, книги и взаимодействия
    all_users = User.objects.all()
    all_books = Book.objects.all()
    all_interactions = Interaction.objects.all()

    # Фильтрация по min_interactions
    # Сначала найдём пользователей и книги, у которых количество взаимодействий >= min_interactions
    from django.db.models import Count

    # Пользователи с min_interactions
    active_users = (
        all_interactions.values("user_id")
        .annotate(interaction_count=Count("user_id"))
        .filter(interaction_count__gte=args.min_interactions)
        .order_by("-interaction_count")[: args.max_users]
    )
    active_user_ids = [user["user_id"] for user in active_users]
    users = User.objects.filter(id__in=active_user_ids)

    # Книги с min_interactions
    popular_books = (
        all_interactions.values("book_id")
        .annotate(interaction_count=Count("book_id"))
        .filter(interaction_count__gte=args.min_interactions)
        .order_by("-interaction_count")[: args.max_books]
    )
    popular_book_ids = [book["book_id"] for book in popular_books]
    books = Book.objects.filter(id__in=popular_book_ids)

    # Взаимодействия только для выбранных пользователей и книг
    interactions = all_interactions.filter(user_id__in=active_user_ids, book_id__in=popular_book_ids)

    # Строим граф
    G = build_filtered_graph(users, books, interactions, args.min_interactions)

    # Применяем алгоритмы
    if args.pagerank:
        top_books = apply_pagerank(G, args.user_id)
        for book_id in top_books:
            if book_id in G:
                G.nodes[book_id]["color"] = "orange"
                for neighbor in G.neighbors(book_id):
                    G.edges[book_id, neighbor]["color"] = "orange"

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
                G.nodes[rec["book"].id]["color"] = "green"
                G.nodes[rec["book"].id]["label"] += f"\n({rec['predicted_rating']:.2f})"
                for neighbor in G.neighbors(rec["book"].id):
                    G.edges[rec["book"].id, neighbor]["color"] = "green"

    # Визуализация с указанным DPI
    visualize_graph(G, args.output, dpi=args.dpi)


if __name__ == "__main__":
    main()