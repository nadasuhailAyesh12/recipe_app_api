
from django.test import TestCase
from django.contrib.auth import get_user_model

from recipe.serializers import (
 RecipeSerializer,
 RecipeDetailSerializer,
)
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import (
    Recipe,
    Tag,
    )
from decimal import Decimal

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    defaults = {
     "title": "sample recipe",
     "time_minutes": 5,
     "price": 5.00,
     "description": "sample recipe description",
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        other_user = create_user(
            email="other@example.com",
            password="test123"
        )
        create_recipe(user=self.user)
        create_recipe(user=other_user)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)
        serializer = RecipeDetailSerializer(recipe)
        res = self.client.get(detail_url(recipe.id))

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_recipe(self):
        payload = {
            "title": "Sample recipe",
            "time_minutes": 30,
            "price": Decimal('5.99')
        }
        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link=original_link)

        payload = {
            "title": "New recipe title",
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_full_update(self):
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link='https://exmaple.com/recipe.pdf',
            description='Sample recipe description.',
            )

        payload = {
            "title": "New recipe title",
            "description": "New recipe description",
            "link": "https://example.com/new-recipe.pdf",
            "time_minutes": 30,
            "price": Decimal('2.99')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        recipe.refresh_from_db()
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(serializer.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_returns_error(self):
        new_user = create_user(
            email="new@example.com",
            password="newpass123"
            )
        recipe = create_recipe(user=self.user)
        payload = {
            "user": new_user.id
        }
        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe(self):
        new_user = create_user(
            email="new@example.com",
            password="newpass123"
        )
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        payload = {
          "title": "sample recipe",
          "time_minutes": 5,
          "price": Decimal("5.00"),
          "tags": [{
            "name": 'Thai'
           },
            {
             "name": 'Dinner'
           }
           ]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        print("nada", res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        """Can be implemented better later
        """
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        print(recipe.tags)
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            print("t", tag)
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 5,
            'price': Decimal("5.00"),
            'tags': [{
                'name': 'Indian'
            },
                 {
                 'name': 'Dinner'
                 }]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        """Can be implemented better later
        """
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertIn(tag_indian, recipe.tags.all())
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        recipe = create_recipe(self.user)
        payload = {
            'tags': [{
                'name': 'Lunch'
                 }]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name="Lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        recipe = create_recipe(self.user)
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        payload = {
            'tags': [{
                'name': 'Lunch'
                 }]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        recipe = create_recipe(user=self.user)
        tag = Tag.objects.create(user=self.user, name="Dessert")
        recipe.tags.add(tag)
        payload = {'tags': []}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
