from rest_framework.serializers import ModelSerializer

from api.models import Source, Fact, Alias, Tag, TagType, Period


class SourceSerializer(ModelSerializer):
    class Meta:
        model = Source
        fields = ('id', 'name', 'accessed', 'author', 'publisher', 'published', 'facts')


class PeriodSerializer(ModelSerializer):
    class Meta:
        model = Period
        fields = ('id', 'start', 'end')


class TagTypeSerializer(ModelSerializer):
    class Meta:
        model = TagType
        fields = ('id', 'name')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'text', 'type', 'tags')


class AliasSerializer(ModelSerializer):
    class Meta:
        model = Alias
        fields = ('id', 'name', 'tag')


class FactSerializer(ModelSerializer):
    class Meta:
        model = Fact
        fields = ('id', 'key', 'value', 'context', 'period', 'tags', 'sources')
