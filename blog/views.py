from pprint import pprint

from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView, DetailView
from elasticsearch_dsl.query import MultiMatch, Q as elastic_Q
from redisearch import Client
from taggit.models import Tag

from blog.documents import PostDocument
from blog.forms import EmailPostForm, CommentForm, SearchForm
from blog.models import Post
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


# from elasticsearch_dsl import connections
#
# # Elasticsearch_dsl
# connections.create_connection(hosts=['localhost'], timeout=20)


# class PostList(ListView):
#     template_name = 'blog/post/list.html'
#     # model = Post
#     queryset = Post.published.all()
#     paginate_by = 5

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 10)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag
                   })


class PostDetail(DetailView):
    model = Post


def post_detail(request, year, month, day, post_slug):
    post = Post.objects.filter(slug=post_slug, status='published')[0]
    print('post')
    print(post.publish)
    post = get_object_or_404(Post, slug=post_slug,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             )

    comments = post.comments.filter(active=True)
    comment_added = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            comment_added = True
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request=request, template_name='blog/post/detail.html', context={'post': post,
                                                                                   'comments': comments,
                                                                                   'comment_form': comment_form,
                                                                                   'comment_added': comment_added,
                                                                                   'similar_posts': similar_posts})


def redirect_to_post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    return redirect(post.get_absolute_url())


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cleaned_data["name"]} {cleaned_data["email"]}, recommends you reading {post.title} '
            message = f'read "{post.title}" at {post_url}\n\n\'s comments: {cleaned_data["comments"]}'
            send_mail(subject=subject, message=message, from_email='admin@email.com',
                      recipient_list=[cleaned_data['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request=request, template_name='blog/post/share.html', context={'post': post,
                                                                                  'form': form,
                                                                                  'sent': sent})


def search(request):
    client = Elasticsearch()

    s = Search(using=client)

    search_result = []
    # pprint(request.POST['query'])
    form = SearchForm(request.POST)
    if form.is_valid():
        # search_result = PostDocument.search().filter('match', )
        search_result = Search().using(client).query(
            elastic_Q('bool', must=[elastic_Q('match', title=request.POST['query'])]))
        for result in search_result:
            pprint(result.body)

    context = {
        'form': form,
        'search_result': search_result
    }
    return render(request=request, template_name='blog/search.html', context=context)


def redisearch(request):
    # TODO: This View Should be in AJAX mode
    # TODO: Implement Autocomplete Feature with Redisearch
    client = Client('blog_index')
    res = client.search("search engine")

    search_result = []
    # pprint(request.POST['query'])
    form = SearchForm(request.POST)
    if form.is_valid():
        # search_result = PostDocument.search().filter('match', )
        search_result = client.search(request.POST['query'])
        if len(search_result.docs) != 0:
            search_result = search_result.docs
        else:
            search_result = []

    context = {
        'form': form,
        'search_result': search_result
    }
    return render(request=request, template_name='blog/redisearch.html', context=context)
