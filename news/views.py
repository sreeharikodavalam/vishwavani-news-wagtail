from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from .models import NewsCategory, NewsTopic, NewsPage, VideoPage
from .models.authors import Author


def category_view(request, category_slug):
    category = get_object_or_404(NewsCategory, slug=category_slug)
    news_list = NewsPage.objects.live().filter(categories=category).order_by('-first_published_at')

    paginator = Paginator(news_list, 12)  # Show 12 news items per page
    page = request.GET.get('page')
    news_items = paginator.get_page(page)

    return render(request, 'news/category_page.html', {
        'category': category,
        'news_items': news_items,
    })


def topic_view(request, topic_slug):
    topic = get_object_or_404(NewsTopic, slug=topic_slug)
    news_list = NewsPage.objects.live().filter(topics=topic).order_by('-first_published_at')

    paginator = Paginator(news_list, 12)
    page = request.GET.get('page')
    news_items = paginator.get_page(page)

    return render(request, 'news/topic_page.html', {
        'topic': topic,
        'news_items': news_items,
    })


def author_view(request, author_slug):
    author = get_object_or_404(Author, slug=author_slug)
    news_list = NewsPage.objects.live().filter(author=author).order_by('-first_published_at')

    paginator = Paginator(news_list, 12)
    page = request.GET.get('page')
    news_items = paginator.get_page(page)

    return render(request, 'news/author_page.html', {
        'author': author,
        'news_items': news_items,
    })


def archive_view(request):
    # Filter parameters
    year = request.GET.get('year')
    month = request.GET.get('month')
    category = request.GET.get('category')

    news_list = NewsPage.objects.live()

    if year:
        news_list = news_list.filter(first_published_at__year=year)
    if month:
        news_list = news_list.filter(first_published_at__month=month)
    if category:
        news_list = news_list.filter(categories__slug=category)

    news_list = news_list.order_by('-first_published_at')

    paginator = Paginator(news_list, 12)
    page = request.GET.get('page')
    news_items = paginator.get_page(page)

    return render(request, 'news/archive_page.html', {
        'news_items': news_items,
        'selected_year': year,
        'selected_month': month,
        'selected_category': category,
    })


def search_view(request):
    query = request.GET.get('q', '')
    news_items = []

    if query:
        news_items = NewsPage.objects.live().search(query)

    return render(request, 'news/search_results.html', {
        'query': query,
        'news_items': news_items,
    })


def breaking_news_view(request):
    news_items = NewsPage.objects.live().filter(is_breaking_news=True).order_by('-first_published_at')

    paginator = Paginator(news_items, 12)
    page = request.GET.get('page')
    news_items = paginator.get_page(page)

    return render(request, 'news/breaking_news_page.html', {
        'news_items': news_items,
    })


def trending_news_view(request):
    news_items = NewsPage.objects.live().order_by('-view_count')[:30]  # Top 30 trending articles

    return render(request, 'news/trending_news_page.html', {
        'news_items': news_items,
    })


def news_index(request):
    news_list = NewsPage.objects.live().order_by('-first_published_at')

    paginator = Paginator(news_list, 12)
    page = request.GET.get('page')
    news_items = paginator.get_page(page)

    return render(request, 'news/news_index_page.html', {
        'news_items': news_items,
    })


def video_index(request):
    videos = VideoPage.objects.live().order_by('-first_published_at')

    paginator = Paginator(videos, 12)  # 12 videos per page
    page = request.GET.get('page')
    video_items = paginator.get_page(page)

    return render(request, 'news/video_index_page.html', {
        'video_items': video_items,
    })
