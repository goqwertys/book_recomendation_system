import numpy as np
from django.core.cache import cache
from sklearn.metrics.pairwise import cosine_similarity

from books.models import Book
from config.settings import CACHE_ENABLED, CACHE_TIMEOUT
from interactions.models import Interaction


def user_based_collaborative_filtering(user_id, k=5, top_n=10):
    cache_key = f"user_recommendations_{user_id}_{k}_{top_n}"

    if CACHE_ENABLED:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

    # Receive all interactions
    interactions = Interaction.objects.all()

    # Building a user-book matrix
    users = list(set(interactions.values_list('user_id', flat=True)))
    books = list(set(interactions.values_list('book_id', flat=True)))

    # Create an empty matrix
    user_book_matrix = np.zeros((len(users), len(books)))

    # Filling in the matrix
    user_to_index = {user_id: i for i, user_id in enumerate(users)}
    book_to_index = {book_id: i for i, book_id in enumerate(books)}

    for interaction in interactions:
        user_idx = user_to_index[interaction.user_id]
        book_idx = book_to_index[interaction.book_id]
        user_book_matrix[user_idx, book_idx] = interaction.rating or 0.0

    # Calculating similarity between users
    user_similarity = cosine_similarity(user_book_matrix)

    # Find the k most similar users
    target_user_idx = user_to_index[user_id]
    similar_users = np.argsort(user_similarity[target_user_idx])[-k - 1:-1][::-1]

    # Predicting ratings
    predicted_ratings = np.zeros(len(books))
    for book_idx in range(len(books)):
        if user_book_matrix[target_user_idx, book_idx] == 0:
            numerator = sum(user_similarity[target_user_idx, user_idx] * user_book_matrix[user_idx, book_idx]
                            for user_idx in similar_users if user_book_matrix[user_idx, book_idx] != 0)
            denominator = sum(user_similarity[target_user_idx, user_idx] for user_idx in similar_users)

            if denominator:
                predicted_ratings[book_idx] = numerator / denominator

    # Recommending books with the highest predicted ratings
    recommended_books_indices = np.argsort(predicted_ratings)[-top_n:][::-1]
    recommended_books_ids = [books[idx] for idx in recommended_books_indices]
    books_queryset = Book.objects.filter(id__in=recommended_books_ids).select_related('author')
    books_dict = {book.id: book for book in books_queryset}

    recommendations = [
        {
            "book": books_dict[book_id],
            "predicted_rating": predicted_ratings[books.index(book_id)]
        }
        for book_id in recommended_books_ids
    ]

    if CACHE_ENABLED:
        cache.set(cache_key, recommendations, timeout=CACHE_TIMEOUT)

    return recommendations
