import random

from django.core.management import BaseCommand
from django.db.models import Avg
from django.utils import timezone

from books.models import Genre, Author, Book
from interactions.models import Interaction
from users.models import User


class Command(BaseCommand):
    help = 'Generates test data for recommendation algorithms'
    base_genres = [

    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_books',
            type=int,
            default=100,
            help='Number of books to create (default: 100)',
        )
        parser.add_argument(
            '--num_users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)',
        )
        parser.add_argument(
            '--num_authors',
            type=int,
            default=20,
            help='Number of users to create (default: 50)',
        )

    def handle(self, *args, **options):
        num_books = options['num_books']
        num_users = options['num_users']
        num_authors = options['num_authors']

        self.stdout.write('Deleting old data...')
        Genre.objects.all().delete()
        Author.objects.all().delete()
        Book.objects.all().delete()
        User.objects.all().delete()
        Interaction.objects.all().delete()

        self.stdout.write('Creating genres...')
        # genres creation
        genres = [
            'Speculative fiction', 'Detective', 'Novel', 'Science',
            'History', 'Fantasy', 'Thriller', 'Biography'
        ]

        genre_objects = [Genre(name=name) for name in genres]
        Genre.objects.bulk_create(genre_objects)
        genres = Genre.objects.all()

        # authors creation
        self.stdout.write(f'Creating {num_authors} authors...')
        authors = [Author(name=f'Author {i}', bio=f'Author {i} Bio') for i in range(1, num_authors + 1)]
        Author.objects.bulk_create(authors)
        authors = Author.objects.all()

        # books creation
        self.stdout.write(f'Creating {num_books} books...')
        books = []
        for i in range(1, num_books + 1):
            book = Book(
                title=f'Book {i}',
                author=random.choice(authors),
                description=f'Description for Book {i}',
                publish_date=timezone.now().date()
            )
            books.append(book)
        Book.objects.bulk_create(books)

        # Adding Genres to Books
        self.stdout.write('Adding Genres to Books...')
        all_books = Book.objects.all()
        for book in all_books:
            book.genres.add(*random.sample(list(genres), k=random.randint(1, 3)))

        # Creating Users
        self.stdout.write('Creating Users...')
        for i in range(1, num_users + 1):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                password='testpass123'
            )
            user.preferred_genres.add(*random.sample(list(genres), k=random.randint(2, 4)))

        # Creating interactions
        self.stdout.write('Creating interactions...')
        interactions = []
        all_books = list(Book.objects.all())
        all_users = User.objects.all()

        for user in all_users:
            user_preferred_genres = user.preferred_genres.all()
            preferred_books = Book.objects.filter(genres__in=user_preferred_genres).distinct()
            other_books = Book.objects.exclude(genres__in=user_preferred_genres).distinct()

            num_interactions = random.randint(10, 21)
            num_preferred = int(num_interactions * 0.7)
            num_other = num_interactions - num_preferred

            try:
                preferred_sample = random.sample(list(preferred_books), num_preferred)
                other_sample = random.sample(list(other_books), num_other)
            except ValueError:
                continue

            for book in preferred_sample + other_sample:
                rating = random.choices(
                    [None, round(random.uniform(3.0, 5.0), 1)],
                    weights=[0.3, 0.7]
                )[0]

                interactions.append(Interaction(
                    user=user,
                    book=book,
                    rating=rating,
                ))

        Interaction.objects.bulk_create(interactions)

        # Updating average ratings
        self.stdout.write('Updating average ratings...')
        books_to_update = Book.objects.filter(interaction__isnull=False).distinct()
        for book in books_to_update:
            book.average_rating = Interaction.objects.filter(book=book).aggregate(
                Avg('rating')
            )['rating__avg'] or 0.0
            book.save()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created:\n'
            f'- {Genre.objects.count()} genres\n'
            f'- {Author.objects.count()} authors\n'
            f'- {Book.objects.count()} books\n'
            f'- {User.objects.count()} users\n'
            f'- {Interaction.objects.count()} interactions'
        ))
