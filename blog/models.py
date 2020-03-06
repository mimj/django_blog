from pprint import pprint
from random import randint

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker
from redisearch import Client
from taggit.managers import TaggableManager

fakegen = Faker()

STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
)


class PublishedQuerySet(models.Manager):
    def get_queryset(self):
        return super(PublishedQuerySet, self).get_queryset().filter(status='published')


class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, related_name='blog_posts', on_delete=models.CASCADE)
    body = models.TextField(default=fakegen.text)
    publish = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    objects = models.Manager()
    published = PublishedQuerySet()

    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    @staticmethod
    def before_save(sender, instance, **kwargs):
        print('pre_save')
        pprint(instance.status)
        if instance.status == 'published':
            if instance.pk is None:
                instance.publish = timezone.now()
            else:
                post = Post.objects.get(pk=instance.pk)
                if post.status == 'draft':
                    #     print('bbb')
                    instance.publish = timezone.now()

    def save(self, *args, **kwargs):
        pprint('save')
        slug_str = self.title
        self.slug = slugify(slug_str)

        super().save(*args, **kwargs)

    @staticmethod
    def after_save(sender, instance, *args, **kwargs):
        print('post_save')
        try:
            # Creating a client with a given index name
            client = Client('blog_index')

            # Indexing a document
            document = client.add_document(instance.id, title=instance.title, body=instance.body)
            pprint('document')
            pprint(document)
        except Exception as e:
            pprint(e)

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.created.year,
                                                 self.created.strftime('%m'),
                                                 self.created.strftime('%d'),
                                                 self.slug])


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
