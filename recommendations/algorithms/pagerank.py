import networkx as nx

from interactions.models import Interaction


def get_pagerank_recommendations(user_id, G, top_n=10):
    pr = nx.pagerank(G, weight='weight')

    # Filter books that the user has not yet interacted with
    user_books = set(Interaction.objects.filter(user_id=user_id).values_list('book_id', flat=True))

    # Collecting ratings for books
    book_scores = {
        int(node.split('_')[1]): score
        for node, score in pr.items()
        if node.startswith('book_') and int(node.split('_')[1]) not in user_books
    }

    return sorted(book_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
