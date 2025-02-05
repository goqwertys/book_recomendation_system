import networkx as nx
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
