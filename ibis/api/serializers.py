from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, ValidationError

from api.models import Source, Fact, Alias, Tag, TagType, Period


class OwnedModelSerializer(ModelSerializer):
    @property
    def user(self):
        return self.context['request'].user

    def save(self):
        # User is necessary to create the new object, but shouldn't be sent as a serialized field
        self.validated_data['user'] = self.user
        return super().save()

    def _validate_owned(self, value):
        if value.user != self.user:
            raise ValidationError("Accessing another user's objects is forbidden")
        return value

    def _validate_owned_list(self, values):
        return [self._validate_owned(val) for val in values]


class SourceSerializer(OwnedModelSerializer):
    facts = PrimaryKeyRelatedField(many=True, queryset=Fact.objects.all(), required=False)

    class Meta:
        model = Source
        fields = ('id', 'name', 'accessed', 'author', 'publisher', 'published', 'facts')

    def validate_facts(self, value):
        return self._validate_owned_list(value)


class PeriodSerializer(OwnedModelSerializer):
    class Meta:
        model = Period
        fields = ('id', 'start', 'end')

    def validate(self, data):
        if data['start'] > data['end']:
            raise ValidationError('Start must come before end')
        return data


class TagTypeSerializer(OwnedModelSerializer):
    class Meta:
        model = TagType
        fields = ('id', 'name')


class TagSerializer(OwnedModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'text', 'type', 'tags')

    def validate_type(self, value):
        return self._validate_owned(value)

    def validate_tags(self, value):
        return self._validate_owned_list(value)


class AliasSerializer(OwnedModelSerializer):
    class Meta:
        model = Alias
        fields = ('id', 'name', 'tag')

    def validate_tag(self, value):
        return self._validate_owned(value)


class FactSerializer(OwnedModelSerializer):
    class Meta:
        model = Fact
        fields = ('id', 'key', 'value', 'context', 'period', 'tags', 'sources')

    def validate_period(self, value):
        return self._validate_owned(value)

    def validate_context(self, value):
        return self._validate_owned(value)

    def validate_tags(self, value):
        return self._validate_owned_list(value)

    def validate_sources(self, value):
        return self._validate_owned_list(value)
