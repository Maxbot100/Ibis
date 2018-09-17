from django.contrib.auth.models import User
from django.db.models import CharField, Model, DateTimeField, TextField, ForeignKey, ManyToManyField, SET_NULL, CASCADE
from django.utils import timezone


class Source(Model):
    """
    The source of information, e.g. a book or news article

    Object properties:
    name (str): Name of the source document
    accessed (datetime): Date & time that the document was accessed by the user
    author (str): Name of the source author
    publisher (str): Name of the source publisher
    published (str): Date that the source was published
    user (User): Owner of this object

    Foreign objects sets:
    facts (Fact): Facts claimed in this source
    """
    name = CharField(max_length=128)
    accessed = DateTimeField(default=timezone.now)
    author = CharField(max_length=128)
    publisher = CharField(max_length=128)
    published = DateTimeField(null=True, blank=True)
    user = ForeignKey(User, on_delete=CASCADE, related_name='sources', related_query_name='source')


class Period(Model):
    """
    A period of time

    Periods may overlap or take on identical start & end times. These objects only exist for the user to easily change
    the shared time period for multiple facts simultaneously.

    Object properties:
    start (datetime): The beginning of the time period
    end (datetime): The end of the time period
    user (User): Owner of this object

    Foreign object sets:
    facts (Fact): Facts that are tied to this specific period of time
    """
    start = DateTimeField(null=True, blank=True)
    end = DateTimeField(null=True, blank=True)
    user = ForeignKey(User, on_delete=CASCADE, related_name='periods', related_query_name='period')


class TagType(Model):
    """
    Grouping & metadata for tags

    name (str): Human-readable name for the tag type
    """
    name = CharField(max_length=64)
    # Once front-end editing is live, this will likely include a "template" field for rendering tags by type


class Tag(Model):
    """
    Grouping facts based on similar topics/person/locations/etc.

    Object Properties:
    name (str): Human-readable name (unique per user)
    text (str): Long description/discussion of the topic/person/location/etc.
    type (TagType): Type of tag (topic/person/location/etc.)
    user (User): Owner of this object

    Foreign object sets:
    aliases (Alias): Alternate names for this tag
    facts (Fact): Facts that tag this object
    tags (Tag): Related/parent topics
    tagged_by (Tag): Other tags that tag this object
    """
    name = CharField(max_length=64)
    text = TextField()
    type = ForeignKey(TagType, on_delete=SET_NULL, related_name='tags', related_query_name='tag')
    tags = ManyToManyField('self', related_name='tagged_by', symmetrical=False)
    user = ForeignKey(User, on_delete=CASCADE, related_name='tags', related_query_name='tag')

    class Meta:
        unique_together = (('name', 'user'),)


class Alias(Model):
    """
    Aliases for tags

    name (str): Alias (unique per user)
    tag (Tag): Tag referenced by the alias
    user (User): Owner of this object
    """
    name = CharField(max_length=64)
    tag = ForeignKey(Tag, on_delete=CASCADE, related_name='aliases', related_query_name='alias')
    user = ForeignKey(User, on_delete=CASCADE, related_name='aliases', related_query_name='alias')

    class Meta:
        unique_together = (('name', 'user'),)
        verbose_name_plural = "aliases"


class Fact(Model):
    """
    Individual, verifiable, sourced information

    Object properties:
    key (str): Used for identifying similar facts in aggregations (e.g. "population" with the value being a number)
    value (str): The information/claim itself (or string representation of value for key-value facts)
    context (Tag): Optional context prefix for the fact (e.g. context: Rome, key: population, value: 200 leads to the
        fact "Rome - population: 200"). Context is always also included in the "tags" set
    period (Period): Period of time in which the claim takes place
    user (User): Owner of this object

    Foreign object sets:
    tags (Tag): Topics/people/locations/etc. discussed in this fact
    sources (Source): Sources that claim this fact is true
    """

    key = CharField(max_length=128)
    value = CharField(max_length=128)
    context = ForeignKey(Tag, null=True, blank=True, on_delete=CASCADE)
    period = ForeignKey(Period, null=True, blank=True, on_delete=SET_NULL, related_name='facts', related_query_name='fact')
    tags = ManyToManyField(Tag, null=True, blank=True, related_name='facts', related_query_name='fact')
    sources = ManyToManyField(Source, null=True, blank=True, related_name='facts', related_query_name='fact')
    user = ForeignKey(User, on_delete=CASCADE, related_name='facts', related_query_name='fact')
