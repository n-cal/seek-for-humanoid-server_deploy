import json
from unittest import skip
from rest_framework import status
from rest_framework.test import APITestCase
from humanoids.models import Humanoid
from .mock_data import api_mock_data

@skip('skip all humanoids test')
class AllHumanoids(APITestCase):
    
    def setUp(self):
        for humanoid_data in api_mock_data:
            Humanoid.objects.create(**humanoid_data)

    
    def test_all_humanoids_list(self):
        response = self.client.get('/api/humanoids')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = json.loads(response.content).get('results')

        for i, result in enumerate(results):
            self.assertIsNotNone(result.get('id'))
            self.assertEqual(result.get('name'), api_mock_data[i].get('name'))
            self.assertEqual(result.get('surname'), api_mock_data[i].get('surname'))
            self.assertEqual(result.get('country'), api_mock_data[i].get('country'))
            self.assertEqual(result.get('thumbnail_url'), api_mock_data[i].get('thumbnail_url'))
            self.assertIsNone(result.get('address'))
            self.assertIsNone(result.get('bio'))
            self.assertIsNone(result.get('city'))
            self.assertIsNone(result.get('email'))
            self.assertIsNone(result.get('mobile'))
            self.assertIsNone(result.get('phone'))
            self.assertIsNone(result.get('zip_code'))
            self.assertIsNone(result.get('img_url'))

@skip('skip search humanoids')
class SearchHumanoids(APITestCase):

    def setUp(self):
        Humanoid.objects.create(id=1, name='Pippo Ciccio', surname='Rossi', email='pippo@email.it')
        Humanoid.objects.create(id=2, name='Mario', surname='Rossi', email='mrossi@email.it')
        Humanoid.objects.create(id=3, name='Pietro', surname='Bianchi Pieri', email='ros@email.it')
        Humanoid.objects.create(id=4, name='Pietro Piero', surname='Bianchi', email='ptr@email.it', country='Utah')
        Humanoid.objects.create(id=5, name='Jack', surname='Sparrow', email='sparrow@email.com', country='Utah')
        Humanoid.objects.create(id=6, name='Jack', surname='Sparrow', email='jsparr@email.com', country='Alabama')

    
    def test_search_by_name(self):
        query_string = r'search=pippo%20ro'
        response = self.client.get(f'/api/humanoids?{query_string}')
        results = json.loads(response.content).get('results')
        result_names = [hum.get('name') + ' ' + hum.get('surname') for hum in results]
        self.assertEqual(len(result_names), 1)
        self.assertTrue('Pippo Ciccio Rossi' in result_names)

        query_string = r'search=pippo%20rossi%20pi'
        response = self.client.get(f'/api/humanoids?{query_string}')
        results = json.loads(response.content).get('results')
        self.assertEqual(len(results), 0)

        query_string = r'search=rossi'
        response = self.client.get(f'/api/humanoids?{query_string}')
        results = json.loads(response.content).get('results')
        result_names = [hum.get('name') + ' ' + hum.get('surname') for hum in results]
        self.assertEqual(len(result_names), 2)
        self.assertTrue('Pippo Ciccio Rossi' in result_names)
        self.assertTrue('Mario Rossi' in result_names)

        query_string = r'search=Pietro%20Bianchi%20Pi'
        response = self.client.get(f'/api/humanoids?{query_string}')
        results = json.loads(response.content).get('results')
        result_names = [hum.get('name') + ' ' + hum.get('surname') for hum in results]
        self.assertEqual(len(result_names), 2)
        self.assertTrue('Pietro Bianchi Pieri' in result_names)
        self.assertTrue('Pietro Piero Bianchi' in result_names)

    def test_search_by_country(self):
        query_string = r'country=Utah'
        response = self.client.get(f'/api/humanoids?{query_string}')
        results = json.loads(response.content).get('results')
        result_ids = [hum.get('id') for hum in results]
        self.assertEqual(len(result_ids), 2)
        self.assertTrue(4 in result_ids)
        self.assertTrue(5 in result_ids)
    
    def test_search_by_name_and_country(self):
        query_string = r'search=sparr&&country=alabama'
        response = self.client.get(f'/api/humanoids?{query_string}')
        results = json.loads(response.content).get('results')
        self.assertEqual(len(results), 1)
        humanoid_picked = results[0]
        self.assertEqual(humanoid_picked.get('name'), 'Jack')
        self.assertEqual(humanoid_picked.get('surname'), 'Sparrow')
        self.assertEqual(humanoid_picked.get('country'), 'Alabama')

@skip('countries')
class AvailableCountries(APITestCase):

    def setUp(self):
        Humanoid.objects.create(name='Mario', email='a@email.com', country='Iowa')
        Humanoid.objects.create(name='Mario', email='b@email.com', country='Utah')
        Humanoid.objects.create(name='Mario', email='c@email.com', country='Alabama')
        Humanoid.objects.create(name='Mario', email='d@email.com', country='Alabama')
        Humanoid.objects.create(name='Mario', email='e@email.com', country='Utah')
        Humanoid.objects.create(name='Mario', email='f@email.com', country='Alabama')
        Humanoid.objects.create(name='Mario', email='g@email.com', country='Illinois')

    def test_available_countries(self):
        response = self.client.get('/api/countries')
        result_countries = json.loads(response.content)
        self.assertEqual(result_countries, ['Alabama', 'Illinois', 'Iowa', 'Utah'])