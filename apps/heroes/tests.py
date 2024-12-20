from django.test import TestCase, Client

class StatsAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_update_heroes_stats(self):
        response = self.client.get('/heroes/update-heroes-stats/')
        self.assertEqual(response.status_code, 200)
