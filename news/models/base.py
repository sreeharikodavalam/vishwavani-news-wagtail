from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SEOFields(models.Model):
    meta_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Override the page title for SEO"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="The page description for SEO"
    )
    og_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Title for social media sharing"
    )
    og_description = models.TextField(
        blank=True,
        help_text="Description for social media sharing"
    )

    seo_panels = [
        MultiFieldPanel([
            FieldPanel('meta_title'),
            FieldPanel('meta_description'),
            FieldPanel('og_title'),
            FieldPanel('og_description'),
        ], heading="SEO Settings")
    ]

    class Meta:
        abstract = True