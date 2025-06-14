from django.test import TestCase
from django.urls import reverse
from .models import Recipe
from .forms import RecipeForm

# Model Tests
class RecipeModelTest(TestCase):
    def test_recipe_creation(self):
        recipe = Recipe.objects.create(
            title='Test Soup',
            ingredients='Water, Salt',
            instructions='Boil water, add salt.'
        )
        self.assertEqual(str(recipe), 'Test Soup')

# View Tests
class RecipeViewTests(TestCase):
    def setUp(self):
        self.recipe1 = Recipe.objects.create(title='Pasta', ingredients='Noodles', instructions='Boil noodles')
        self.recipe2 = Recipe.objects.create(title='Salad', ingredients='Lettuce', instructions='Mix lettuce')

    # recipe_list view tests
    def test_recipe_list_view_status_code(self):
        response = self.client.get(reverse('recipe_list'))
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_view_uses_correct_template(self):
        response = self.client.get(reverse('recipe_list'))
        self.assertTemplateUsed(response, 'recipes/recipe_list.html')

    def test_recipe_list_view_displays_recipes(self):
        response = self.client.get(reverse('recipe_list'))
        self.assertContains(response, self.recipe1.title)
        self.assertContains(response, self.recipe2.title)

    def test_recipe_list_view_no_recipes(self):
        Recipe.objects.all().delete()
        response = self.client.get(reverse('recipe_list'))
        self.assertContains(response, 'No recipes yet.')

    # create_recipe view tests
    def test_create_recipe_view_get(self):
        response = self.client.get(reverse('create_recipe'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/recipe_form.html')
        self.assertIsInstance(response.context['form'], RecipeForm)

    def test_create_recipe_view_post_valid(self):
        data = {'title': 'New Cake', 'ingredients': 'Flour, Sugar', 'instructions': 'Mix and bake'}
        response = self.client.post(reverse('create_recipe'), data)
        self.assertEqual(response.status_code, 302) # Redirects
        self.assertRedirects(response, reverse('recipe_list'))
        self.assertTrue(Recipe.objects.filter(title='New Cake').exists())

    def test_create_recipe_view_post_invalid(self):
        data = {'title': '', 'ingredients': 'Flour, Sugar', 'instructions': 'Mix and bake'} # Invalid: empty title
        response = self.client.post(reverse('create_recipe'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/recipe_form.html')
        self.assertFalse(Recipe.objects.filter(title='').exists()) # Should not be created
        self.assertTrue(response.context['form'].errors)


    # recipe_detail view tests
    def test_recipe_detail_view_status_code_existing(self):
        response = self.client.get(reverse('recipe_detail', args=[self.recipe1.id]))
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_view_uses_correct_template(self):
        response = self.client.get(reverse('recipe_detail', args=[self.recipe1.id]))
        self.assertTemplateUsed(response, 'recipes/recipe_detail.html')

    def test_recipe_detail_view_displays_recipe_content(self):
        response = self.client.get(reverse('recipe_detail', args=[self.recipe1.id]))
        self.assertContains(response, self.recipe1.title)
        self.assertContains(response, self.recipe1.ingredients)
        self.assertContains(response, self.recipe1.instructions)

    def test_recipe_detail_view_status_code_non_existent(self):
        non_existent_id = self.recipe1.id + self.recipe2.id + 100 # An ID that likely doesn't exist
        response = self.client.get(reverse('recipe_detail', args=[non_existent_id]))
        self.assertEqual(response.status_code, 404)

    # edit_recipe view tests
    def test_edit_recipe_view_get_existing(self):
        response = self.client.get(reverse('edit_recipe', args=[self.recipe1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/recipe_form.html')
        self.assertIsInstance(response.context['form'], RecipeForm)
        self.assertEqual(response.context['form'].instance, self.recipe1)

    def test_edit_recipe_view_get_non_existent(self):
        non_existent_id = self.recipe1.id + self.recipe2.id + 100
        response = self.client.get(reverse('edit_recipe', args=[non_existent_id]))
        self.assertEqual(response.status_code, 404)

    def test_edit_recipe_view_post_valid(self):
        updated_title = 'Updated Pasta Title'
        data = {'title': updated_title, 'ingredients': 'New Ingredients', 'instructions': 'New Instructions'}
        response = self.client.post(reverse('edit_recipe', args=[self.recipe1.id]), data)
        self.assertEqual(response.status_code, 302) # Redirects
        self.assertRedirects(response, reverse('recipe_detail', args=[self.recipe1.id]))
        self.recipe1.refresh_from_db()
        self.assertEqual(self.recipe1.title, updated_title)

    def test_edit_recipe_view_post_invalid(self):
        data = {'title': '', 'ingredients': 'New Ingredients', 'instructions': 'New Instructions'} # Invalid: empty title
        response = self.client.post(reverse('edit_recipe', args=[self.recipe1.id]), data)
        self.assertEqual(response.status_code, 200) # Stays on page
        self.assertTemplateUsed(response, 'recipes/recipe_form.html')
        self.recipe1.refresh_from_db()
        self.assertNotEqual(self.recipe1.title, '') # Title should not have changed to empty
        self.assertTrue(response.context['form'].errors)
