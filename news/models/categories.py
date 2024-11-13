from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from django.utils.text import slugify
from wagtail.snippets.models import register_snippet
from .base import TimestampedModel, SEOFields


@register_snippet
class NewsCategory(TimestampedModel, SEOFields):
    name = models.CharField(
        max_length=100,
        help_text="Category name as it appears on the site"
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL-friendly version of the category name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the category"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        help_text="Parent category if this is a subcategory"
    )
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Icon representing this category"
    )
    featured = models.BooleanField(
        default=False,
        help_text="Feature this category prominently on the site"
    )
    order = models.IntegerField(
        default=0,
        help_text="Order of appearance in menus and lists"
    )
    show_in_menu = models.BooleanField(
        default=True,
        help_text="Show this category in navigation menus"
    )
    layout_choices = [
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
        ('featured', 'Featured Layout')
    ]
    layout = models.CharField(
        max_length=10,
        choices=layout_choices,
        default='grid',
        help_text="Default layout for category pages"
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('description'),
            FieldPanel('parent'),
        ], heading="Basic Information"),

        MultiFieldPanel([
            FieldPanel('icon'),
            FieldPanel('featured'),
            FieldPanel('order'),
            FieldPanel('show_in_menu'),
            FieldPanel('layout'),
        ], heading="Display Options"),
    ]

    panels.extend(SEOFields.seo_panels)  # Add SEO panels to the end

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_hierarchy(self):
        """Returns list of parent categories plus current category"""
        hierarchy = []
        current = self
        while current is not None:
            hierarchy.append(current)
            current = current.parent
        return reversed(hierarchy)

    @property
    def full_name(self):
        """Returns category name including parent names"""
        return ' > '.join(category.name for category in self.get_hierarchy())

    def get_children(self):
        """Returns all immediate child categories"""
        return self.children.filter(show_in_menu=True).order_by('order')

    def get_descendants(self):
        """Returns all descendant categories (recursive)"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    class Meta:
        verbose_name = "News Category"
        verbose_name_plural = "News Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.full_name