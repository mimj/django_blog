# django_blog
blog with django
----------------------
1-start redisearch service (using docker)

2- start elasticsearch service

    to working with elasticsearch(otherwise will not work):
        uncomment @registry.register_document in documents.py
        uncomment 'django_elasticsearch_dsl', in settings.py

3- python manage.py migrate

4- python manage.py seed_db.py

5- python manage.py createsuperuser