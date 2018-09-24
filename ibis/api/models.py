from django.contrib.auth.models import User
from django.db.models import Manager, Model, DateTimeField, CharField, TextField, ForeignKey, ManyToManyField, \
    SET_NULL, CASCADE
from django.urls import reverse
from django.utils import timezone


class APIModel(Model):
    objects: Manager

    class Meta:
        abstract = True
        default_related_name = "%(class)ss"

    def get_absolute_url(self):
        return reverse('{}-detail'.format(self._meta.model_name), kwargs={'pk': self.pk})


class Source(APIModel):
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
    author = CharField(max_length=128, blank=True)
    publisher = CharField(max_length=128, blank=True)
    published = DateTimeField(null=True, blank=True)
    user = ForeignKey(User, on_delete=CASCADE, related_query_name='%(class)s')

    def __str__(self) -> str:
        s = '"{0.name}"'
        if self.author:
            s += " by {0.author}"
        if self.published:
            s += " on {0.published:%Y-%m-%d}"
        return s.format(self)


class Period(APIModel):
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
    user = ForeignKey(User, on_delete=CASCADE, related_query_name='%(class)s')

    def __str__(self) -> str:
        if self.start:
            if self.end:
                return "{0.start:%Y-%m-%d %H:%M:%S} to {0.end:%Y-%m-%d %H:%M:%S}".format(self)
            else:
                return "from {0.start:%Y-%m-%d %H:%M:%S}".format(self)
        elif self.end:
            return "until {0.end:%Y-%m-%d %H:%M:%S}".format(self)
        else:
            return "(unknown period)"


class TagType(APIModel):
    """
    Grouping & metadata for tags

    name (str): Human-readable name for the tag type
    user (User): Owner of this object
    """
    name = CharField(max_length=64)
    user = ForeignKey(User, on_delete=CASCADE, related_query_name='%(class)s')
    # Once front-end editing is live, this will likely include a "template" field for rendering tags by type

    def __str__(self) -> str:
        return str(self.name)


class Tag(APIModel):
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
    text = TextField(blank=True)
    type = ForeignKey(TagType, null=True, blank=True, on_delete=SET_NULL, related_query_name='%(class)s')
    tags = ManyToManyField('self', related_name='tagged_by', symmetrical=False)
    user = ForeignKey(User, on_delete=CASCADE, related_query_name='%(class)s')

    class Meta(APIModel.Meta):
        unique_together = (('name', 'user'),)

    def __str__(self) -> str:
        return str(self.name)


class Alias(APIModel):
    """
    Aliases for tags

    name (str): Alias (unique per user)
    tag (Tag): Tag referenced by the alias
    user (User): Owner of this object
    """
    name = CharField(max_length=64)
    tag = ForeignKey(Tag, on_delete=CASCADE, related_query_name='%(class)s')
    user = ForeignKey(User, on_delete=CASCADE, related_query_name='%(class)s')

    class Meta(APIModel.Meta):
        default_related_name = '%(class)ses'
        unique_together = (('name', 'user'),)
        verbose_name_plural = "aliases"

    def __str__(self) -> str:
        return "{0.name} -> {0.tag.name}".format(self)


class Fact(APIModel):
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
    key = CharField(max_length=128, blank=True)
    value = CharField(max_length=128)
    context = ForeignKey(Tag, null=True, blank=True, on_delete=CASCADE, related_name='contextualized')
    period = ForeignKey(Period, null=True, blank=True, on_delete=SET_NULL, related_query_name='%(class)s')
    tags = ManyToManyField(Tag, blank=True, related_query_name='%(class)s')
    sources = ManyToManyField(Source, blank=True, related_query_name='%(class)s')
    user = ForeignKey(User, on_delete=CASCADE, related_query_name='%(class)s')

    def __str__(self) -> str:
        s = ""
        if self.context:
            s += "{0.context} - "
        if self.key:
            s += "{0.key}: "
        s += "{0.value}"
        return s.format(self)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure context is added to tags. Does nothing if relationship already exists
        if self.context:
            self.tags.add(self.context)
