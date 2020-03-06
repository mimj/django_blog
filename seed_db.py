import os
import sys
from pprint import pprint

import django
import random

# from django_blog import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')

django.setup()

from django.contrib.auth.models import User
from faker.utils.text import slugify
from blog.models import Post
from faker import Faker
from faker.providers import lorem

fakegen = Faker()
fakegen.add_provider(lorem)


def get_user(username):
    user_qs = User.objects.filter(username=username)
    if not user_qs:
        user = User.objects.create_user(
            username=username,
            password='123',
            email=fakegen.email()
        )
    else:
        pprint(user_qs)
        user = user_qs.get()
    return user


def populate(N=5):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    # STATUS_CHOICES = (
    #     'draft',
    #     'published',
    # )
    USER_NAMES = ('jojo', 'dodo', 'roro', 'ioio', 'rere', 'lele', 'veve')
    pprint(random.choice(STATUS_CHOICES))
    pprint(fakegen.date())
    for item in range(N):
        user = get_user(username=random.choice(USER_NAMES))
        post = Post.objects.get_or_create(
            title=fakegen.text(70),
            # slug=slug,
            author=user,
            body=fakegen.text(10000),
            # publish=fakegen.date(),
            # created=fakegen.date(),
            # updated=fakegen.date(),
            status=random.choice(STATUS_CHOICES)[0],
        )
        # post.save()


if __name__ == '__main__':
    # N = sys.argv[1]
    # pprint(N)
    print('started populating')
    populate(40)
    print('finished populating')
