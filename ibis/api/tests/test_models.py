import json
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from api.models import Source, Period, TagType, Tag, Alias, Fact


class ModelTestCase(TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="u", password="p")


class APIModelTestCase(ModelTestCase):
    def test_get_url(self):
        name = 'test_name'
        t = TagType(name=name, user=self.user)
        t.save()
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get(t.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], t.id)
        self.assertEqual(response.data['name'], name)


class SourceTestCase(ModelTestCase):
    def test_str(self):
        name = "test_name"
        author = "test_author"
        published = datetime.now()
        source = Source.objects.create(name=name, user=self.user)
        self.assertIn(name, str(source))
        source.author = author
        self.assertIn(name, str(source))
        self.assertIn(author, str(source))
        source.published = published
        self.assertIn(name, str(source))
        self.assertIn(author, str(source))
        self.assertIn(published.strftime("%Y-%m-%d"), str(source))
        source.author = None
        self.assertIn(name, str(source))
        self.assertIn(published.strftime("%Y-%m-%d"), str(source))


class PeriodTestCase(ModelTestCase):
    def test_str(self):
        start = datetime.now()
        end = datetime.now() - timedelta(days=1000, hours=1, minutes=1, seconds=1)  # ensuring we get different values
        source = Period.objects.create(user=self.user)
        self.assertNotEqual(str(source), "")
        source.start = start
        self.assertIn(start.strftime("%Y-%m-%d %H:%M:%S"), str(source))
        source.end = end
        self.assertIn(start.strftime("%Y-%m-%d %H:%M:%S"), str(source))
        self.assertIn(end.strftime("%Y-%m-%d %H:%M:%S"), str(source))
        source.start = None
        self.assertIn(end.strftime("%Y-%m-%d %H:%M:%S"), str(source))


class TagTypeTestCase(ModelTestCase):
    def test_str(self):
        name = "test_name"
        tag_type = TagType(name=name, user=self.user)
        self.assertIn(name, str(tag_type))


class TagTestCase(ModelTestCase):
    def test_str(self):
        name = "test_name"
        tag = Tag(name=name, user=self.user)
        self.assertIn(name, str(tag))


class AliasTestCase(ModelTestCase):
    def test_str(self):
        alias = "test_alias"
        name = "test_name"
        tag_alias = Alias(name=alias, tag=Tag(name=name, user=self.user), user=self.user)
        self.assertIn(alias, str(tag_alias))
        self.assertIn(name, str(tag_alias))


class FactTestCase(ModelTestCase):
    def test_str(self):
        key = "test_key"
        value = "test_value"
        context = Tag(name='test_name', user=self.user)
        fact = Fact(value=value, user=self.user)
        self.assertIn(value, str(fact))
        fact.context = context
        self.assertIn(value, str(fact))
        self.assertIn(str(context), str(fact))
        fact.key = key
        self.assertIn(value, str(fact))
        self.assertIn(str(context), str(fact))
        self.assertIn(key, str(fact))
        fact.context = None
        self.assertIn(value, str(fact))
        self.assertIn(key, str(fact))

    def test_context_in_tags(self):
        context = Tag(name='test_context', user=self.user)
        context.save()
        fact = Fact(value='test_value', user=self.user)
        fact.save()
        self.assertNotIn(context, list(fact.tags.all()))
        self.assertIsNone(fact.context)
        fact.context = context
        fact.save()
        self.assertIn(context, list(fact.tags.all()))
        self.assertEqual(fact.context, context)
