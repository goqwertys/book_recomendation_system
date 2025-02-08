import numpy as np
from django.core.cache import cache
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import CACHE_ENABLED, CACHE_TIMEOUT
from interactions.models import Interaction
from users.models import User


def find_k_nearest_neighbors(user_id, k=5):
    cache_key = f"user_neighbors_{user_id}_{k}"

    if CACHE_ENABLED:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

    # Get all interactions
    interactions = Interaction.objects.all()

    # Building a user-book matrix
    users = list(set(interactions.values_list('user_id', flat=True)))
    books = list(set(interactions.values_list('book_id', flat=True)))

    if not users or not books:
        return []

    # Filling the matrix
    user_to_index = {user_id: i for i, user_id in enumerate(users)}
    book_to_index = {book_id: i for i, book_id in enumerate(books)}

    if user_id not in user_to_index:
        return []

    # Create an empty matrix
    user_book_matrix = np.zeros((len(users), len(books)))

    for interaction in interactions:
        user_idx = user_to_index[interaction.user_id]
        book_idx = book_to_index[interaction.book_id]
        user_book_matrix[user_idx, book_idx] = interaction.rating or 0.0

    # Calculate the similarity between users
    user_similarity = cosine_similarity(user_book_matrix)

    # Find k nearest neighbors
    target_user_idx = user_to_index[user_id]
    nearest_neighbors = np.argsort(user_similarity[target_user_idx])[-k - 1:-1][::-1]

    if not nearest_neighbors.size:
        return []

    result = User.objects.filter(id__in=[users[idx] for idx in nearest_neighbors])

    if CACHE_ENABLED:
        cache.set(cache_key, result, timeout=CACHE_TIMEOUT)

    return result
