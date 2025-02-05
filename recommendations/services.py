from django.core.cache import cache
from django.db.models import Avg, Count, Q
from django.utils import timezone

from books.models import Book
from config.settings import CACHE_ENABLED, CACHE_TIMEOUT
from recommendations.algorithms import pagerank, collaborative, k_nearest_neighbors
from recommendations.algorithms.collaborative import user_based_collaborative_filtering
from recommendations.graph_builder import build_user_book_graph
from users.models import User


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
    cache_key = f"user_recommendations_{user_id}_{k}_{top_n}"

    if CACHE_ENABLED:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

    recommendations = user_based_collaborative_filtering(user_id, k, top_n)

    if CACHE_ENABLED:
        cache.set(cache_key, recommendations, timeout=CACHE_TIMEOUT)

    return recommendations


def get_knn_recommendations_service(user_id, k=5):
    cache_key = f'user_recommendation_knn_{user_id}_{k}'

    if CACHE_ENABLED:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

    k_neighbors = k_nearest_neighbors.find_k_nearest_neighbors(user_id, k)

    if CACHE_ENABLED:
        cache.set(cache_key, k_neighbors, timeout=CACHE_TIMEOUT)

    return k_neighbors


def get_statistics():
    # Check cache
    if CACHE_ENABLED:
        cached_data = cache.get('statistics')
        if cached_data:
            return cached_data

    # Total number of books
    books_count = Book.objects.all().count()

    # Total number of users
    users_count = User.objects.all().count()

    # Number of new books per week
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    new_books_week_count = Book.objects.filter(publish_date__gte=one_week_ago).count()

    # Top 5 Popular Books with the Highest Average Rating
    top_rated_books = Book.objects.annotate(
        avg_rating=Avg('interaction__rating'),
        rating_count=Count('interaction__rating')
    ).order_by('-avg_rating', '-rating_count')[:5]

    # Top 5 most active users (most interactions per week)
    top_active_users = User.objects.annotate(
        interaction_count=Count(
            'interaction',
            filter=Q(interaction__timestamp__gte=one_week_ago)
        )
    ).order_by('-interaction_count')[:5]

    # Forming data
    statistics_data = {
        'books_count': books_count,
        'users_count': users_count,
        'new_books_week_count': new_books_week_count,
        'top_rated_books': top_rated_books,
        'top_active_users': top_active_users
    }

    # Data caching
    if CACHE_ENABLED:
        cache.set('statistics', statistics_data, CACHE_TIMEOUT)

    return statistics_data
