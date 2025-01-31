from django.db import models


NULLABLE = {
    'blank': True,
    'null': True
}


class Genre(models.Model):
    """ Genre model """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Author(models.Model):
    """ Author model """
    name = models.CharField(max_length=100)
    bio = models.TextField()

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.name


class Book(models.Model):
    """ Book model """
    title = models.CharField(max_length=100)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    description = models.TextField(**NULLABLE)
    cover = models.ImageField(
        upload_to='books/'
    )
    genres = models.ManyToManyField('Genre')
    publish_data = models.DateField()

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title
