# news/management/commands/generate_sample_data.py
import random
from io import BytesIO

import requests
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker
from wagtail.images.models import Image

from news.models import NewsCategory, NewsTopic
from news.models.authors import Author

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Generates sample data for the news portal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--news',
            type=int,
            default=50,
            help='Number of news articles to generate'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting sample data generation...')

        # # Create categories
        # self.create_categories()
        #
        # # Create topics
        # self.create_topics()
        #
        # # Create authors
        # self.create_authors()

        # Create news articles
        self.create_news(options['news'])

        self.stdout.write(self.style.SUCCESS('Sample data generation completed!'))

    def download_image(self, category):
        """Download a random image from Unsplash"""
        try:
            # Use Unsplash source for random images based on category
            url = f"https://source.unsplash.com/800x600/?{category}"
            response = requests.get(url)
            if response.status_code == 200:
                return BytesIO(response.content)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error downloading image: {e}'))
        return None

    def create_image(self, title, category):
        """Create a Wagtail image"""
        image_io = self.download_image(category)
        if image_io:
            image = Image(title=title)
            image.file.save(f"{title}.jpg", ContentFile(image_io.getvalue()))
            return image
        return None

    def create_categories(self):
        """Create sample categories"""
        categories = [
            ("ರಾಜ್ಯ", "state", "State news coverage"),
            ("ರಾಷ್ಟ್ರೀಯ", "national", "National news coverage"),
            ("ಅಂತರರಾಷ್ಟ್ರೀಯ", "international", "International news"),
            ("ಕ್ರೀಡೆ", "sports", "Sports coverage"),
            ("ವಾಣಿಜ್ಯ", "business", "Business news"),
            ("ಸಿನಿಮಾ", "entertainment", "Entertainment news"),
            ("ರಾಜಕೀಯ", "politics", "Political news"),
            ("ತಂತ್ರಜ್ಞಾನ", "technology", "Technology news"),
            ("ಆರೋಗ್ಯ", "health", "Health news"),
            ("ಶಿಕ್ಷಣ", "education", "Education news")
        ]

        for name, slug, desc in categories:
            category, created = NewsCategory.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slug,
                    'description': desc,
                    'icon': self.create_image(f"Category-{slug}", slug)
                }
            )
            if created:
                self.stdout.write(f'Created category: {name}')

    def create_topics(self):
        """Create sample topics"""
        topics = [
            "ಬೆಂಗಳೂರು", "ಮೈಸೂರು", "COVID-19", "ಚುನಾವಣೆ",
            "ಕ್ರಿಕೆಟ್", "ಸಿನಿಮಾ", "ಹವಾಮಾನ", "ಶಿಕ್ಷಣ",
            "ರಾಜಕೀಯ", "ಆರ್ಥಿಕತೆ", "ಕ್ರೀಡೆ", "ತಂತ್ರಜ್ಞಾನ"
        ]

        for topic_name in topics:
            topic, created = NewsTopic.objects.get_or_create(
                name=topic_name,
                defaults={
                    'slug': fake.slug(),
                    'description': fake.paragraph(),
                    'featured_image': self.create_image(f"Topic-{topic_name}", topic_name)
                }
            )
            if created:
                self.stdout.write(f'Created topic: {topic_name}')

    def create_authors(self):
        """Create sample authors"""
        for _ in range(10):
            name = fake.name()
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123'
            )

            author, created = Author.objects.get_or_create(
                user=user,
                defaults={
                    'name': name,
                    'slug': fake.slug(),
                    'bio': fake.paragraph(),
                    'designation': random.choice([
                        'Senior Editor', 'Staff Writer', 'Correspondent',
                        'Special Correspondent', 'Contributing Editor'
                    ]),
                    'profile_image': self.create_image(f"Author-{name}", "portrait")
                }
            )
            if created:
                self.stdout.write(f'Created author: {name}')

    def create_news(self, count):
        """Create sample news articles with robust hierarchy and initialization checks."""
        from wagtail.models import Page
        from news.models import NewsIndexPage, NewsPage
        from django.utils import timezone
        from datetime import timedelta
        import random
        import json

        # Fetch categories, topics, and authors
        categories = list(NewsCategory.objects.all())
        topics = list(NewsTopic.objects.all())
        authors = list(Author.objects.all())

        # Ensure the root page exists and fetch it
        root_page = Page.get_first_root_node()
        if not root_page:
            self.stdout.write(self.style.ERROR("Root page not found. Ensure Wagtail is set up correctly."))
            return

        # Delete existing NewsIndexPage if it exists to reset
        news_index = NewsIndexPage.objects.first()
        if news_index:
            news_index.delete()
            self.stdout.write(self.style.WARNING("Deleted existing News Index Page"))

        # Create a fresh NewsIndexPage under root_page
        news_index = NewsIndexPage(
            title="News",
            slug="news",
            intro="Latest news and updates"
        )
        root_page.add_child(instance=news_index)
        news_index.save_revision().publish()
        news_index.refresh_from_db()
        self.stdout.write(self.style.SUCCESS("Re-created News Index Page"))

        # Confirm that NewsIndexPage has a valid path and depth
        self.stdout.write(f"News Index Page path: {news_index.path}, depth: {news_index.depth}")
        if not news_index.path or not news_index.depth:
            self.stdout.write(self.style.ERROR("News Index Page is not correctly initialized in the hierarchy."))
            return

        # Sample Kannada titles for articles
        kannada_sentences = [
            "ಬೆಂಗಳೂರು: ಮುಖ್ಯಮಂತ್ರಿ ಘೋಷಣೆ",
            "ಮೈಸೂರು: ದಸರಾ ಆಚರಣೆಗೆ ಸಜ್ಜು",
            "ಹುಬ್ಬಳ್ಳಿ: ರೈತರ ಪ್ರತಿಭಟನೆ",
            "ಮಂಗಳೂರು: ಮಳೆ ಅಬ್ಬರ",
            "ದೆಹಲಿ: ಸಂಸತ್ ಅಧಿವೇಶನ ಆರಂಭ",
            "ಶಿವಮೊಗ್ಗ: ಶಾಲೆಗಳಿಗೆ ರಜೆ ಘೋಷಣೆ",
            "ಬೆಳಗಾವಿ: ವಿಧಾನಸಭೆ ಅಧಿವೇಶನ",
            "ಗುಲ್ಬರ್ಗ: ಕೃಷಿ ಮೇಳ ಯಶಸ್ವಿ",
            "ಬೆಂಗಳೂರು: ಮೆಟ್ರೋ ವಿಸ್ತರಣೆ",
            "ಚಿಕ್ಕಮಗಳೂರು: ಕಾಫಿ ಬೆಳೆಗಾರರ ಸಮಸ್ಯೆ"
        ]

        # Create articles as children of NewsIndexPage
        for i in range(count):
            publish_date = timezone.now() - timedelta(days=random.randint(0, 180))

            title = random.choice(kannada_sentences)
            intro = fake.paragraph()

            body_data = [
                {"type": "paragraph", "value": fake.paragraph()},
                {"type": "paragraph", "value": fake.paragraph()}
            ]

            article = NewsPage(
                title=title,
                slug=f"news-{i + 1}",
                intro=intro,
                body=json.dumps(body_data),
                author=random.choice(authors),
                is_breaking_news=random.choice([True, False] + [False] * 8),
                is_featured=random.choice([True, False] + [False] * 4),
                first_published_at=publish_date
            )

            try:
                news_index.add_child(instance=article)
                article.save()
                article.categories.add(*random.sample(categories, random.randint(1, 3)))
                article.topics.add(*random.sample(topics, random.randint(1, 4)))
                article.save_revision().publish()
                self.stdout.write(f"Created article: {title}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to add article '{title}': {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"Successfully attempted to create {count} news articles"))
