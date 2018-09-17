from django.contrib.auth.models import User
from django.db.models import Manager, Model, DateTimeField, CharField, TextField, ForeignKey, ManyToManyField, \
    SET_NULL, CASCADE
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
    objects: Manager

    name = CharField(max_length=128)
    accessed = DateTimeField(default=timezone.now)
    author = CharField(max_length=128, blank=True)
    publisher = CharField(max_length=128, blank=True)
    published = DateTimeField(null=True, blank=True)
    user = ForeignKey(User, on_delete=CASCADE, related_name='sources', related_query_name='source')

    def __str__(self) -> str:
        return "{0.name} by {0.author} on {0.published}".format(self)


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
    objects: Manager

    start = DateTimeField(null=True, blank=True)
    end = DateTimeField(null=True, blank=True)
    user = ForeignKey(User, on_delete=CASCADE, related_name='periods', related_query_name='period')

    def __str__(self) -> str:
        if self.start:
            if self.end:
                return "{0.start:%Y-%m-%d %H:%M:%S} to {0.end:%Y-%m-%d %H:%M:%S}".format(self)
            else:
                return "from {0.start:%Y-%m-%d %H:%M:%S}".format(self)
        elif self.end:
            return "until {0.end:%Y-%m-%d %H:%M:%S}".format(self)
        else:
            #
            return "(unknown period)"


class TagType(Model):
    """
    Grouping & metadata for tags

    name (str): Human-readable name for the tag type
    """
    objects: Manager

    name = CharField(max_length=64)

    # Once front-end editing is live, this will likely include a "template" field for rendering tags by type

    def __str__(self) -> str:
        return str(self.name)


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
    objects: Manager

    name = CharField(max_length=64)
    text = TextField()
    type = ForeignKey(TagType, on_delete=SET_NULL, related_name='tags', related_query_name='tag')
    tags = ManyToManyField('self', related_name='tagged_by', symmetrical=False)
    user = ForeignKey(User, on_delete=CASCADE, related_name='tags', related_query_name='tag')

    class Meta:
        unique_together = (('name', 'user'),)

    def __str__(self) -> str:
        return str(self.name)


class Alias(Model):
    """
    Aliases for tags

    name (str): Alias (unique per user)
    tag (Tag): Tag referenced by the alias
    user (User): Owner of this object
    """
    objects: Manager

    name = CharField(max_length=64)
    tag = ForeignKey(Tag, on_delete=CASCADE, related_name='aliases', related_query_name='alias')
    user = ForeignKey(User, on_delete=CASCADE, related_name='aliases', related_query_name='alias')

    class Meta:
        unique_together = (('name', 'user'),)
        verbose_name_plural = "aliases"

    def __str__(self) -> str:
        return "{0.name} -> {0.tag.name}".format(self)


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
    objects: Manager

    key = CharField(max_length=128, blank=True)
    value = CharField(max_length=128)
    context = ForeignKey(Tag, null=True, blank=True, on_delete=CASCADE)
    period = ForeignKey(Period, null=True, blank=True, on_delete=SET_NULL, related_name='facts',
                        related_query_name='fact')
    tags = ManyToManyField(Tag, null=True, blank=True, related_name='facts', related_query_name='fact')
    sources = ManyToManyField(Source, null=True, blank=True, related_name='facts', related_query_name='fact')
    user = ForeignKey(User, on_delete=CASCADE, related_name='facts', related_query_name='fact')

    def __str__(self) -> str:
        s = ""
        if self.context:
            s += "{0.context} - ".format(self)
        if self.key:
            s += "{0.key}: ".format(self)
        s += self.value
        return s

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure context is added to tags. Does nothing if relationship already exists
        self.tags.add(self.context)
