import networkx as nx
from django.db.models import Count

from books.models import Book
from interactions.models import Interaction
from users.models import User


def build_user_book_graph():
    """ Builds User-Book graph based on Interactions """
    G = nx.Graph()

    # Adding nodes for users and books
    for user in User.objects.all():
        G.add_node(f'user_{user.id}', type='user')

    for book in Book.objects.all():
        G.add_node(f'book_{book.id}', type='book')


    # Adding edges based on interactions
    for interaction in Interaction.objects.select_related('user', 'book'):
        user_node = f'user_{interaction.user.id}'
        book_node = f'book_{interaction.book.id}'
        weight = interaction.rating if interaction.rating else 0.5
        G.add_edge(user_node, book_node, weight=weight)

    return G


def build_filtered_graph(max_users=30, max_books=50, min_book_interactions=1):
    """Builds a user-book graph with data filtering"""
    G = nx.Graph()

    # Filtering data
    users = User.objects.annotate(num_interactions=Count('interaction')).order_by('-num_interactions')[:max_users]
    books = Book.objects.annotate(num_interactions=Count('interaction')).filter(
        num_interactions__gte=min_book_interactions
    ).order_by('-num_interactions')[:max_books]

    if not users:
        raise ValueError("No users found to display")
    if not books:
        raise ValueError("No books found matching the criteria you specified")

    # Adding nodes
    for user in users:
        G.add_node(
            f'user_{user.id}',
            label=f'User {user.id}',
            color='#3B7BFF',
            shape='ellipse',
            size=25,
            level=1
        )

    for book in books:
        truncated_title = book.title[:20] + '...' if len(book.title) > 20 else book.title
        G.add_node(
            f'book_{book.id}',
            label=truncated_title,
            color='#FF6B3B',
            shape='box',
            size=20,
            level=2
        )

    # Adding links
    for interaction in Interaction.objects.filter(user__in=users, book__in=books).select_related('user', 'book'):
        weight = interaction.rating or 0.5
        G.add_edge(f'user_{interaction.user.id}', f'book_{interaction.book.id}', weight=weight)

    if len(G.edges) == 0:
        print("Warning: No interactions between selected users and books")

    # Cleaning isolated nodes
    G.remove_nodes_from(list(nx.isolates(G)))

    return G
