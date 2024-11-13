from django import forms
from django.contrib.auth.models import User
from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from django.utils import timezone
from datetime import timedelta

from .blocks import ContentBlock
from .base import SEOFields
from .categories import NewsCategory
from .topics import NewsTopic
from .authors import Author


class NewsIndexPage(Page):
    """Landing page for all news articles."""
    intro = RichTextField(
        blank=True,
        help_text="Introduction text for the news section"
    )

    featured_categories = models.ManyToManyField(
        'news.NewsCategory',
        blank=True,
        related_name='featured_index_pages',
        help_text="Select categories to feature on this page"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('featured_categories', widget=forms.CheckboxSelectMultiple),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get published news articles
        news_items = NewsPage.objects.child_of(self).live()

        # Filter by category if specified
        category_slug = request.GET.get('category')
        if category_slug:
            news_items = news_items.filter(categories__slug=category_slug)

        # Filter by topic if specified
        topic_slug = request.GET.get('topic')
        if topic_slug:
            news_items = news_items.filter(topics__slug=topic_slug)

        # Filter by date range if specified
        date_filter = request.GET.get('date')
        if date_filter:
            if date_filter == 'today':
                news_items = news_items.filter(first_published_at__date=timezone.now().date())
            elif date_filter == 'week':
                week_ago = timezone.now() - timedelta(days=7)
                news_items = news_items.filter(first_published_at__gte=week_ago)
            elif date_filter == 'month':
                month_ago = timezone.now() - timedelta(days=30)
                news_items = news_items.filter(first_published_at__gte=month_ago)

        # Order news items
        news_items = news_items.order_by('-first_published_at')

        # Add items to context
        context.update({
            'news_items': news_items,
            'featured_news': news_items.filter(is_featured=True)[:5],
            'breaking_news': news_items.filter(is_breaking_news=True)[:5],
            'trending_news': news_items.order_by('-view_count')[:5],
        })

        return context

    class Meta:
        verbose_name = "News Landing Page"


def get_default_author():
    # First, get or create a system user
    system_user, _ = User.objects.get_or_create(
        username='system',
        defaults={
            'email': 'system@vishwavani.news',
            'first_name': 'Vishwavani',
            'last_name': 'News'
        }
    )

    # Then get or create the author using that user
    default_author, _ = Author.objects.get_or_create(
        user=system_user,
        defaults={
            'name': 'Vishwavani News',
            'slug': 'vishwavani-news',
            'is_featured': False,
            'designation': 'System Account'
        }
    )

    return default_author.id

class NewsPage(Page, SEOFields):
    """Individual news article page."""

    # Basic Content
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        help_text="A secondary headline"
    )
    intro = models.TextField(
        help_text="News article introduction or summary"
    )
    body = StreamField(
        ContentBlock(),
        use_json_field=True,
        help_text="Main article content"
    )

    # Media
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Main image for the article"
    )
    image_caption = models.CharField(
        max_length=250,
        blank=True,
        help_text="Caption for the featured image"
    )

    # Organization & Classification
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name='articles',
        default=get_default_author,
        help_text="Select the article author"
    )
    categories = models.ManyToManyField(
        NewsCategory,
        related_name='articles',
        help_text="Select relevant categories"
    )
    topics = models.ManyToManyField(
        NewsTopic,
        related_name='articles',
        help_text="Select relevant topics"
    )

    # Publishing Options
    is_breaking_news = models.BooleanField(
        default=False,
        help_text="Mark as breaking news"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this article on landing pages"
    )
    is_premium = models.BooleanField(
        default=False,
        help_text="Mark as premium content"
    )
    allow_comments = models.BooleanField(
        default=True,
        help_text="Enable reader comments"
    )

    # Source Attribution
    source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Original source if this is syndicated content"
    )
    source_url = models.URLField(
        blank=True,
        help_text="Link to original article if syndicated"
    )

    # Metrics
    read_time = models.PositiveIntegerField(
        default=0,
        help_text="Estimated reading time in minutes"
    )
    view_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Number of times this article has been viewed"
    )

    # Search configuration
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.FilterField('author'),
        index.FilterField('first_published_at'),
        index.FilterField('view_count'),
    ]

    # Admin panels configuration
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('subtitle'),
            FieldPanel('intro'),
            FieldPanel('body'),
        ], heading="Content"),

        MultiFieldPanel([
            FieldPanel('featured_image'),
            FieldPanel('image_caption'),
        ], heading="Featured Image"),

        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
            FieldPanel('topics', widget=forms.CheckboxSelectMultiple),
        ], heading="Organization"),

        MultiFieldPanel([
            FieldPanel('is_breaking_news'),
            FieldPanel('is_featured'),
            FieldPanel('is_premium'),
            FieldPanel('allow_comments'),
        ], heading="Publishing Options"),

        MultiFieldPanel([
            FieldPanel('source'),
            FieldPanel('source_url'),
        ], heading="Source Attribution"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('meta_title'),
            FieldPanel('meta_description'),
            FieldPanel('og_title'),
            FieldPanel('og_description'),
        ], heading="SEO and Social")
    ]

    def save(self, *args, **kwargs):
        # Calculate reading time before saving
        if self.body:
            word_count = len(str(self.body).split())
            self.read_time = max(1, round(word_count / 200))  # Assuming 200 words per minute

        super().save(*args, **kwargs)

    def serve(self, request):
        # Increment view count on each page view
        self.view_count += 1
        self.save(update_fields=['view_count'])
        return super().serve(request)

    def get_absolute_url(self):
        return self.url

    def get_related_articles(self, limit=3):
        """Get related articles based on categories and topics."""
        related = NewsPage.objects.live().filter(
            models.Q(categories__in=self.categories.all()) |
            models.Q(topics__in=self.topics.all())
        ).exclude(id=self.id).distinct()
        return related[:limit]

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def __str__(self):
        return self.title