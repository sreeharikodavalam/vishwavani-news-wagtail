from django.db import models
from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from django.utils.text import slugify

User = get_user_model()


@register_snippet
class Author(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='author_profile'
    )
    name = models.CharField(
        max_length=100,
        help_text="Author's display name"
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        blank=True,
        help_text="URL-friendly version of the name"
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Author's role or position"
    )
    bio = models.TextField(
        blank=True,
        help_text="Brief biography of the author"
    )
    profile_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this author on the website"
    )

    # Social Media Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    # Analytics
    article_count = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)

    panels = [
        MultiFieldPanel([
            FieldPanel('user'),
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('designation'),
            FieldPanel('bio'),
            FieldPanel('profile_image'),
            FieldPanel('is_featured'),
        ], heading="Basic Information"),

        MultiFieldPanel([
            FieldPanel('facebook_url'),
            FieldPanel('twitter_url'),
            FieldPanel('instagram_url'),
            FieldPanel('youtube_url'),
        ], heading="Social Media"),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_article_count(self):
        """Update the count of published articles by this author"""
        from .pages import NewsPage
        self.article_count = NewsPage.objects.live().filter(author=self).count()
        self.save(update_fields=['article_count'])

    def get_absolute_url(self):
        return f'/authors/{self.slug}/'

    def get_recent_articles(self, limit=5):
        """Get recent articles by this author"""
        from .pages import NewsPage
        return NewsPage.objects.live().filter(author=self).order_by('-first_published_at')[:limit]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ['-article_count', 'name']