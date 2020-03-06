from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from .models import Post

# TODO: remove Comment From Decorator and django elasticsearch in settings
# @registry.register_document
class PostDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'posts'

    class Django:
        model = Post  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'title',
            'body',
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000
