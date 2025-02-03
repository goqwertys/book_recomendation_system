from django.core.cache import cache

from config.settings import CACHE_ENABLED
from recommendations.algorithms import pagerank, collaborative, k_nearest_neighbors
from recommendations.graph_builder import build_user_book_graph


def get_pagerank_recommendations_service(user_id, top_n=10):
    if not CACHE_ENABLED:
        G = build_user_book_graph()
    else:
        key = 'user_book_graph'
        G = cache.get(key)
        if not G:
            G = build_user_book_graph()
            cache.set('user_book_graph', G, timeout=3600)

    return pagerank.get_pagerank_recommendations(user_id, G, top_n)


def get_collaborative_recommendations_service(user_id, k=5, top_n=10):
    return collaborative.user_based_collaborative_filtering(user_id, k, top_n)


def get_knn_recommendations_service(user_id, k=5):
    return k_nearest_neighbors.find_k_nearest_neighbors(user_id, k)
