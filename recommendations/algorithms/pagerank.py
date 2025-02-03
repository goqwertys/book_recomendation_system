import networkx as nx

from books.models import Book
from interactions.models import Interaction


def get_pagerank_recommendations(user_id, G, top_n=10):
    """ Returns top_n for books for user_id's user via PageRank algorithm from a given graph """
    pr = nx.pagerank(G, weight='weight')

    # Filter books that the user has not yet interacted with
    user_books = set(Interaction.objects.filter(user_id=user_id).values_list('book_id', flat=True))

    # Collecting ratings for books
    book_scores = {
        int(node.split('_')[1]): score
        for node, score in pr.items()
        if node.startswith('book_') and int(node.split('_')[1]) not in user_books
    }

    top_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    books = Book.objects.filter(id__in=[book_id for book_id, _ in top_books]).select_related('author')

    return [{"book": book, "score": book_scores[book.id]} for book in books]
