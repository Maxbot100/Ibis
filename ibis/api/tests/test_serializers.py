from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Model
from django.http import HttpRequest
from django.utils import timezone
from rest_framework.test import APITestCase

from api.models import Tag, TagType, Source, Fact, Alias
from api.serializers import TagSerializer, SourceSerializer, AliasSerializer, PeriodSerializer


class SerializerTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.password = "test_pass"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username='u2', password='p2')

    def _test_cross_user(self, cls: type, obj: Model, ref: Model, key: str, is_list: bool):
        """
        Tests that adding a reference to another user's object should fail
        :param cls: Serializer class
        :param obj: Object to be serialized
        :param ref: Reference to add, with a different user than obj
        :param key: Attribute field name for the reference
        :param is_list: Whether to treat it as a single reference or single-item list of references
        """
        obj.save()
        ref.save()
        request = HttpRequest()
        request.user = self.user
        if is_list:
            data = {key: [ref.pk]}
        else:
            data = {key: ref.pk}
        serializer = cls(obj, data=data, partial=True, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.keys(), {key})
        self.assertEqual(len(serializer.errors[key]), 1)
        self.assertIn("forbidden", serializer.errors[key][0])

    def _test_same_user(self, cls: type, obj: Model, ref: Model, key: str, is_list: bool):
        """
        Tests that adding a reference to another user's object should fail
        :param cls: Serializer class
        :param obj: Object to be serialized
        :param ref: Reference to add, with the same user as obj
        :param key: Attribute field name for the reference
        :param is_list: Whether to treat it as a single reference or single-item list of references
        """
        obj.save()
        ref.save()
        request = HttpRequest()
        request.user = self.user
        if is_list:
            data = {key: [ref.pk]}
        else:
            data = {key: ref.pk}
        serializer = cls(obj, data=data, partial=True, context={'request': request})
        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        if is_list:
            self.assertEqual(getattr(obj, key).get(pk=ref.pk), ref)
        else:
            self.assertEqual(getattr(obj, key), ref)


class SourceTestCase(SerializerTestCase):
    def test_cross_user_facts(self):
        self._test_cross_user(
            SourceSerializer,
            Source(name='s', user=self.user),
            Fact(value='f', user=self.user2),
            'facts', is_list=True
        )

    def test_same_user_facts(self):
        self._test_same_user(
            SourceSerializer,
            Source(name='s', user=self.user),
            Fact(value='f', user=self.user),
            'facts', is_list=True
        )

    def test_create(self):
        name = 's'
        request = HttpRequest()
        request.user = self.user
        serializer = SourceSerializer(data={'name': name}, context={'request': request})
        self.assertTrue(serializer.is_valid())
        source = serializer.save()
        # Ensure the database matches what we saved
        self.assertEqual(Source.objects.get(pk=source.pk), source)
        self.assertEqual(Source.objects.get(pk=source.pk).name, name)


class PeriodTestCase(SerializerTestCase):
    def test_period_order(self):
        start = timezone.now()
        end = start - timedelta(days=1)
        request = HttpRequest()
        request.user = self.user
        serializer = PeriodSerializer(data={'start': start, 'end': end}, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.keys(), {'non_field_errors'})
        self.assertEqual(len(serializer.errors['non_field_errors']), 1)
        self.assertIn("start", serializer.errors['non_field_errors'][0].lower())
        self.assertIn("end", serializer.errors['non_field_errors'][0].lower())


class TagTestCase(SerializerTestCase):
    def test_cross_user_tag(self):
        self._test_cross_user(
            TagSerializer,
            Tag(name='t1', user=self.user),
            Tag(name='t2', user=self.user2),
            'tags', is_list=True
        )

    def test_same_user_tag(self):
        self._test_same_user(
            TagSerializer,
            Tag(name='t1', user=self.user),
            Tag(name='t2', user=self.user),
            'tags', is_list=True
        )

    def test_cross_user_type(self):
        self._test_cross_user(
            TagSerializer,
            Tag(name='t1', user=self.user),
            TagType(name='type', user=self.user2),
            'type', is_list=False
        )

    def test_same_user_type(self):
        self._test_same_user(
            TagSerializer,
            Tag(name='t1', user=self.user),
            TagType(name='type', user=self.user),
            'type', is_list=False
        )


class AliasTestCase(SerializerTestCase):
    def test_cross_user_tag(self):
        tag = Tag(name='t2', user=self.user2)
        tag.save()
        request = HttpRequest()
        request.user = self.user
        serializer = AliasSerializer(data={'name': 't1', 'tag': tag.pk}, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.keys(), {'tag'})
        self.assertEqual(len(serializer.errors['tag']), 1)
        self.assertIn("forbidden", serializer.errors['tag'][0])
