from django import forms
from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from news.models import NewsTopic, NewsPage


# Custom blocks for homepage sections
class FeaturedNewsBlock(blocks.StructBlock):
    title = blocks.CharBlock(default="Featured News")
    news_count = blocks.IntegerBlock(default=4)
    categories = blocks.ListBlock(blocks.PageChooserBlock(page_type='news.NewsPage'))
    display_style = blocks.ChoiceBlock(choices=[
        ('slider', 'Slider'),
        ('grid', 'Grid'),
        ('featured', 'Featured with Sidebar')
    ], default='slider')

    class Meta:
        template = 'blocks/featured_news.html'
        icon = 'pick'


class CategoryNewsBlock(blocks.StructBlock):
    category = blocks.PageChooserBlock(page_type='news.NewsCategory')
    news_count = blocks.IntegerBlock(default=4)
    display_style = blocks.ChoiceBlock(choices=[
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
        ('compact', 'Compact Layout')
    ], default='grid')

    class Meta:
        template = 'blocks/category_news.html'
        icon = 'folder-open-inverse'


class VideoNewsBlock(blocks.StructBlock):
    title = blocks.CharBlock(default="Latest Videos")
    video_count = blocks.IntegerBlock(default=4)
    display_style = blocks.ChoiceBlock(choices=[
        ('grid', 'Grid'),
        ('carousel', 'Carousel')
    ], default='carousel')

    class Meta:
        template = 'blocks/video_news.html'
        icon = 'media'


class AuthorShowcaseBlock(blocks.StructBlock):
    title = blocks.CharBlock(default="Our Authors")
    author_count = blocks.IntegerBlock(default=6)
    display_style = blocks.ChoiceBlock(choices=[
        ('grid', 'Grid'),
        ('carousel', 'Carousel')
    ], default='carousel')

    class Meta:
        template = 'blocks/author_showcase.html'
        icon = 'user'


class AdBlock(blocks.StructBlock):
    ad_code = blocks.RawHTMLBlock()
    placement_id = blocks.CharBlock(help_text="Unique identifier for this ad placement")

    class Meta:
        template = 'blocks/advertisement.html'
        icon = 'plus'


class HomePage(Page):
    # Header Settings
    show_breaking_news = models.BooleanField(
        default=True,
        help_text="Show breaking news ticker"
    )
    breaking_news_count = models.IntegerField(default=5)

    show_trending_topics = models.BooleanField(
        default=True,
        help_text="Show trending topics bar"
    )

    featured_categories = models.ManyToManyField(
        'news.NewsCategory',
        blank=True,
        related_name='featured_on_home',
        help_text="Categories to show in main navigation"
    )

    # Main Content - Making it nullable and providing a default empty list
    content_sections = StreamField([
        ('featured_news', FeaturedNewsBlock()),
        ('category_news', CategoryNewsBlock()),
        ('video_news', VideoNewsBlock()),
        ('author_showcase', AuthorShowcaseBlock()),
        ('advertisement', AdBlock()),
    ], use_json_field=True, blank=True, null=True, default=[])  # Added these parameters

    # Sidebar Settings
    show_weather_widget = models.BooleanField(
        default=True,
        help_text="Show weather widget in sidebar"
    )

    show_trending_sidebar = models.BooleanField(
        default=True,
        help_text="Show trending news in sidebar"
    )

    show_popular_categories = models.BooleanField(
        default=True,
        help_text="Show popular categories in sidebar"
    )

    # Social Media Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('show_breaking_news'),
            FieldPanel('breaking_news_count'),
            FieldPanel('show_trending_topics'),
            FieldPanel('featured_categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Header Settings"),

        FieldPanel('content_sections'),

        MultiFieldPanel([
            FieldPanel('show_weather_widget'),
            FieldPanel('show_trending_sidebar'),
            FieldPanel('show_popular_categories'),
        ], heading="Sidebar Settings"),

        MultiFieldPanel([
            FieldPanel('facebook_url'),
            FieldPanel('twitter_url'),
            FieldPanel('instagram_url'),
            FieldPanel('youtube_url'),
        ], heading="Social Media Links"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add breaking news if enabled
        if self.show_breaking_news:
            from news.models import NewsPage  # Import here to avoid circular import
            context['breaking_news'] = NewsPage.objects.live().filter(
                is_breaking_news=True
            ).order_by('-first_published_at')[:self.breaking_news_count]

        # Add trending topics if enabled
        if self.show_trending_topics:
            context['trending_topics'] = NewsTopic.objects.order_by(
                '-view_count'  # Sort by views instead
            )[:10]

        return context

    def get_state_news(self):
        return NewsPage.objects.live().filter(
            categories__slug='state'
        ).order_by('-first_published_at')

    def get_national_news(self):
        return NewsPage.objects.live().filter(
            categories__slug='national'
        ).order_by('-first_published_at')

    def get_international_news(self):
        return NewsPage.objects.live().filter(
            categories__slug='international'
        ).order_by('-first_published_at')

    @property
    def featured_news(self):
        return NewsPage.objects.live().filter(
            is_featured=True
        ).order_by('-first_published_at')[:5]

    class Meta:
        verbose_name = "Home Page"
