from django.db import models
from django import forms
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index

from .base import SEOFields
from .categories import NewsCategory
from .topics import NewsTopic
import urllib.parse


class VideoIndexPage(Page):
    """Index page for listing all videos"""
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # Get all videos
        context['full_videos'] = VideoPage.objects.live().child_of(self).filter(
            video_type='full').order_by('-first_published_at')
        context['shorts'] = VideoPage.objects.live().child_of(self).filter(
            video_type='short').order_by('-first_published_at')
        return context

    class Meta:
        verbose_name = "Video Index Page"


class VideoPage(Page, SEOFields):
    """Model for both full videos and shorts"""

    # Video Type Choice
    VIDEO_TYPES = [
        ('full', 'Full Video'),
        ('short', 'Short Video')
    ]
    video_type = models.CharField(
        max_length=5,
        choices=VIDEO_TYPES,
        default='full',
        help_text="Select the type of video content"
    )

    # Video Content
    youtube_url = models.URLField(
        help_text="Full URL of the YouTube video"
    )
    duration = models.PositiveIntegerField(
        help_text="Duration in seconds",
        null=True,
        blank=True
    )
    description = RichTextField(
        help_text="Full description of the video"
    )
    transcript = models.TextField(
        blank=True,
        help_text="Video transcript (optional)"
    )

    # Thumbnail
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Thumbnail image for the video"
    )

    # Organization
    categories = models.ManyToManyField(
        NewsCategory,
        blank=True,
        related_name='videos',
        help_text="Categories this video belongs to"
    )
    topics = models.ManyToManyField(
        NewsTopic,
        blank=True,
        related_name='videos',
        help_text="Topics covered in this video"
    )

    # Metrics
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this video has been viewed"
    )

    # Publishing Options
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this video prominently"
    )
    is_trending = models.BooleanField(
        default=False,
        help_text="Mark as trending"
    )

    # Properties
    @property
    def youtube_id(self):
        """Extract YouTube video ID from URL"""
        parsed_url = urllib.parse.urlparse(self.youtube_url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return urllib.parse.parse_qs(parsed_url.query)['v'][0]
            if parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
        return None

    @property
    def embed_url(self):
        """Generate embed URL for the video"""
        if self.youtube_id:
            return f'https://www.youtube.com/embed/{self.youtube_id}'
        return None

    @property
    def formatted_duration(self):
        """Format duration in HH:MM:SS"""
        if self.duration:
            hours = self.duration // 3600
            minutes = (self.duration % 3600) // 60
            seconds = self.duration % 60
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            return f"{minutes}:{seconds:02d}"
        return None

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('video_type'),
            FieldPanel('youtube_url'),
            FieldPanel('duration'),
            FieldPanel('description'),
            FieldPanel('transcript'),
        ], heading="Video Details"),

        MultiFieldPanel([
            FieldPanel('thumbnail'),
        ], heading="Thumbnail"),

        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
            FieldPanel('topics', widget=forms.CheckboxSelectMultiple),
        ], heading="Organization"),

        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_trending'),
        ], heading="Publishing Options"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('meta_title'),
            FieldPanel('meta_description'),
        ], heading="SEO"),
    ]

    # Search config
    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('transcript'),
        index.FilterField('video_type'),
        index.FilterField('first_published_at'),
    ]

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self):
        return f"{self.title} ({'Short' if self.video_type == 'short' else 'Full Video'})"

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])