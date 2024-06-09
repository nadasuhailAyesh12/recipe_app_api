from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagSerializer
from core.models import Tag

TAGS_URL = reverse('recipe:tag-list')


def create_user(email="test@example.com", password="testpass123"):
    return get_user_model().objects.create_user(email, password)


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_reuired(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tags_limited_to_user(self):
        other_user = create_user(email="user2@example.com")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")
        Tag.objects.create(user=other_user, name="Fruity")

        res = self.client.get(TAGS_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        payload = {
           'name': 'Dessert'
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
