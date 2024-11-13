from datetime import timedelta

from django import forms
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from .base import TimestampedModel, SEOFields


@register_snippet
class NewsTopic(TimestampedModel, SEOFields):
    name = models.CharField(
        max_length=100,
        help_text="Topic name as it appears on the site"
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL-friendly version of the topic name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this topic covers"
    )
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Featured image for topic landing page"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this topic prominently on the site"
    )
    is_trending = models.BooleanField(
        default=False,
        help_text="Mark this topic as trending"
    )
    related_topics = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Other topics that are related to this one"
    )

    # Analytics and Tracking
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this topic has been viewed"
    )
    follower_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of users following this topic"
    )
    article_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of articles tagged with this topic"
    )

    # RSS Feed Settings
    include_in_feed = models.BooleanField(
        default=True,
        help_text="Include this topic in RSS feeds"
    )
    feed_description = models.TextField(
        blank=True,
        help_text="Custom description for topic RSS feed"
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('description'),
            FieldPanel('featured_image'),
        ], heading="Basic Information"),

        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_trending'),
            FieldPanel('related_topics', widget=forms.CheckboxSelectMultiple),
        ], heading="Display Options"),

        MultiFieldPanel([
            FieldPanel('include_in_feed'),
            FieldPanel('feed_description'),
        ], heading="RSS Feed Settings"),

        MultiFieldPanel([
            FieldPanel('view_count', read_only=True),
            FieldPanel('follower_count', read_only=True),
            FieldPanel('article_count', read_only=True),
        ], heading="Analytics", classname="collapsed")
    ]

    # Add SEO panels at the end
    panels.extend(SEOFields.seo_panels)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/topics/{self.slug}/'

    def increment_view_count(self):
        """Increment the view count for this topic"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_follower_count(self):
        """Increment the follower count for this topic"""
        self.follower_count += 1
        self.save(update_fields=['follower_count'])

    def decrement_follower_count(self):
        """Decrement the follower count for this topic"""
        if self.follower_count > 0:
            self.follower_count -= 1
            self.save(update_fields=['follower_count'])

    def update_article_count(self):
        """Update the count of articles tagged with this topic"""
        from .pages import NewsPage  # Import here to avoid circular import
        self.article_count = NewsPage.objects.filter(topics=self).count()
        self.save(update_fields=['article_count'])

    def get_related_articles(self, limit=5):
        """Get related articles for this topic"""
        from .pages import NewsPage  # Import here to avoid circular import
        return NewsPage.objects.live().filter(
            topics=self
        ).order_by('-first_published_at')[:limit]

    def get_trending_articles(self, days=7, limit=5):
        """Get trending articles for this topic within specified days"""
        from .pages import NewsPage
        start_date = timezone.now() - timedelta(days=days)
        return NewsPage.objects.live().filter(
            topics=self,
            first_published_at__gte=start_date
        ).order_by('-view_count')[:limit]

    class Meta:
        verbose_name = "News Topic"
        verbose_name_plural = "News Topics"
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name
