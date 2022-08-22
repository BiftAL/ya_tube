from django.test import Client, TestCase


class ViewTestClass(TestCase):

    def setUp(self):
        self.client = Client()

    def test_error_page_404_status(self):
        """Несуществующая страница возвращает статус 404"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)

    def test_error_page_404_template(self):
        """Несуществующая страница(404) использует правильный шаблон"""
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
