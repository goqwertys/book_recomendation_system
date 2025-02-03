import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from interactions.models import Interaction


def find_k_nearest_neighbors(user_id, k=5):
    # Get all interactions
    interactions = Interaction.objects.all()

    # Building a user-book matrix
    users = set(interactions.values_list('user_id', flat=True))
    books = set(interactions.values_list('book_id', flat=True))

    # Create an empty matrix
    user_book_matrix = np.zeros((len(users), len(books)))

    # Filling the matrix
    user_to_index = {user_id: i for i, user_id in enumerate(users)}
    book_to_index = {book_id: i for i, book_id in enumerate(books)}

    for interaction in interactions:
        user_idx = user_to_index[interaction.user_id]
        book_idx = book_to_index[interaction.book_id]
        user_book_matrix[user_idx, book_idx] = interaction.rating if interaction.rating else 0.0

    # Replace NaN with 0
    user_book_matrix = np.nan_to_num(user_book_matrix, nan=0.0)

    # Calculate the similarity between users
    user_similarity = cosine_similarity(user_book_matrix)

    # Find k nearest neighbors
    target_user_idx = user_to_index[user_id]
    nearest_neighbors = np.argsort(user_similarity[target_user_idx])[-k - 1:-1][::-1]

    nearest_neighbor_ids = [list(users)[user_idx] for user_idx in nearest_neighbors]
    return nearest_neighbor_ids
