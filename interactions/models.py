from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

import books.models
import users.models


NULLABLE = {
    'blank': True,
    'null': True
}


class Interaction(models.Model):
    """ Interaction model """
    user = models.ForeignKey(users.models.User, on_delete=models.CASCADE)
    book = models.ForeignKey(books.models.Book, on_delete=models.CASCADE)

    rating = models.FloatField(
        **NULLABLE,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    viewed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Interaction'
        verbose_name_plural = 'Interactions'
        unique_together = (('user', 'book'),)
        indexes = [
            models.Index(fields=['user', 'book'])
        ]
