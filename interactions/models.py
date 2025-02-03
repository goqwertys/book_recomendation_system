from django.core.exceptions import PermissionDenied
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

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
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Interaction'
        verbose_name_plural = 'Interactions'
        unique_together = (('user', 'book'),)
        indexes = [
            models.Index(fields=['user', 'book'])
        ]

    def save(self, *args, **kwargs):
        """
        Overridden save method to update the average rating of a book.
        """
        if self.pk:
            original = Interaction.objects.get(pk=self.pk)
            if original.user != self.user:
                raise PermissionDenied("You can't change someone else's interactions.")
        super().save(*args, **kwargs)
        self.book.average_rating = Interaction.objects.filter(book=self.book).aggregate(
            Avg('rating')
        )['rating__avg'] or 0.0

        self.book.save()
