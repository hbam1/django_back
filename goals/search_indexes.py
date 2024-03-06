from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import *

@registry.register_document
class GoalDocument(Document):
    class Index:
        name = 'goals'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'region': fields.TextField(),
        'region_detail': fields.TextField(),
    })

    tags = fields.NestedField(properties={
        'tag_id': fields.Integer(),
    })

    activity_tags = fields.NestedField(properties={
        'tag_id': fields.Integer(),
    })

    class Django:
        model = Goal
        fields = [
            'favor_offline',
            'title',
            'content',
            'is_in_group',
            'is_completed',
        ]

    def prepare_tags(self, instance):
        return [{'tag_id': tag.pk} for tag in instance.tags.all()]

    def prepare_activity_tags(self, instance):
        return [{'tag_id': tag.pk} for tag in instance.activity_tags.all()]