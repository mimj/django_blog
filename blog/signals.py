from pprint import pprint

from django.core.signals import request_finished
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from blog.models import Post

pre_save.connect(Post.before_save, sender=Post, dispatch_uid="before_save")
post_save.connect(Post.after_save, sender=Post, dispatch_uid='after_save')
