from datetime import timedelta

from django import template
from django.db.models import Count
from django.utils import timezone

from ..models import NewsPage, NewsCategory
from ..models.authors import Author

register = template.Library()


@register.simple_tag
def get_trending_news(limit=5):
    """Get trending news articles based on view count in last 7 days"""
    seven_days_ago = timezone.now() - timedelta(days=7)
    return NewsPage.objects.live().filter(
        first_published_at__gte=seven_days_ago
    ).order_by('-view_count')[:limit]


@register.simple_tag
def get_breaking_news(limit=5):
    """Get breaking news articles"""
    return NewsPage.objects.live().filter(
        is_breaking_news=True
    ).order_by('-first_published_at')[:limit]


@register.simple_tag
def get_category_news(category_slug, limit=5):
    """Get news articles from a specific category"""
    return NewsPage.objects.live().filter(
        categories__slug=category_slug
    ).order_by('-first_published_at')[:limit]


@register.simple_tag
def get_topic_news(topic_slug, limit=5):
    """Get news articles for a specific topic"""
    return NewsPage.objects.live().filter(
        topics__slug=topic_slug
    ).order_by('-first_published_at')[:limit]


@register.simple_tag
def get_popular_categories(limit=10):
    """Get categories with most articles"""
    return NewsCategory.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count')[:limit]


@register.simple_tag
def get_featured_authors(limit=6):
    """Get featured authors"""
    return Author.objects.filter(
        is_featured=True
    ).order_by('-article_count')[:limit]


@register.simple_tag
def get_related_articles(article, limit=3):
    """Get related articles based on categories and topics"""
    return article.get_related_articles(limit=limit)


@register.simple_tag(takes_context=True)
def get_breadcrumbs(context):
    """Generate breadcrumbs for current page"""
    page = context.get('page')
    if not page:
        return []

    breadcrumbs = []
    while page:
        breadcrumbs.insert(0, page)
        page = page.get_parent()
    return breadcrumbs


@register.filter
def time_since(value):
    """Return time since article was published"""
    now = timezone.now()
    diff = now - value

    if diff.days > 7:
        return value.strftime("%B %d, %Y")
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"
