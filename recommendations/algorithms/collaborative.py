import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from interactions.models import Interaction


def user_based_collaborative_filtering(user_id, k=5, top_n=10):
    # We receive all interactions
    interactions = Interaction.objects.all()

    # Building a user-book matrix
    users = set(interactions.values_list('user_id', flat=True))
    books = set(interactions.values_list('book_id', flat=True))

    # Create an empty matrix
    user_book_matrix = np.zeros((len(users), len(books)))

    # Filling in the matrix
    user_to_index = {user_id: i for i, user_id in enumerate(users)}
    book_to_index = {book_id: i for i, book_id in enumerate(books)}

    for interaction in interactions:
        user_idx = user_to_index[interaction.user_id]
        book_idx = book_to_index[interaction.book_id]
        user_book_matrix[user_idx, book_idx] = interaction.rating if interaction.rating else 0.0

    # Replace NaN with 0
    user_book_matrix = np.nan_to_num(user_book_matrix, nan=0.0)

    # Calculating similarity between users
    user_similarity = cosine_similarity(user_book_matrix)

    # Find the k most similar users
    target_user_idx = user_to_index[user_id]
    similar_users = np.argsort(user_similarity[target_user_idx])[-k - 1:-1][::-1]

    # Predicting ratings
    predicted_ratings = np.zeros(len(books))
    for book_idx in range(len(books)):
        if user_book_matrix[target_user_idx, book_idx] == 0:  # Книга не оценена
            numerator = 0
            denominator = 0
            for user_idx in similar_users:
                if user_book_matrix[user_idx, book_idx] != 0:
                    numerator += user_similarity[target_user_idx, user_idx] * user_book_matrix[user_idx, book_idx]
                    denominator += user_similarity[target_user_idx, user_idx]
            if denominator != 0:
                predicted_ratings[book_idx] = numerator / denominator

    # Recommending books with the highest predicted ratings
    recommended_books = np.argsort(predicted_ratings)[-top_n:][::-1]
    return [(list(books)[book_idx], predicted_ratings[book_idx]) for book_idx in recommended_books]
