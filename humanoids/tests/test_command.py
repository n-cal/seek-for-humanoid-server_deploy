from humanoids.models import Humanoid
from django.test import TestCase
from unittest import mock, skip
from django.core.management import call_command
from core.settings import BASE_DIR
from humanoids.management.commands.pullhumanoids import HumanoidImagesGenerator
import time

from .mock_data import command_mock_data, mock_image_in_bytes

path_to_command = 'humanoids.management.commands.pullhumanoids'

@skip('skip command')
class StoreHumanoids(TestCase):

    @mock.patch(
            path_to_command + '.HumanoidImagesGenerator.create_humanoid_images', 
            return_value=['primary_img.jpg', 'thumbnail.jpg']
        )
    @mock.patch(path_to_command + '.fetch_humanoids_data', return_value=command_mock_data)
    def test_humanoids_pull(self, mock_fetch_humanoids_data, mock_create_humanoid_images):
        call_command('pullhumanoids')

        for mock_data in command_mock_data:
            humanoid = Humanoid.objects.get(email=mock_data['email'])
            self.assertEqual(humanoid.address, mock_data['address'])
            self.assertEqual(humanoid.bio, mock_data['bio'])
            self.assertEqual(humanoid.city, mock_data['city'])
            self.assertEqual(humanoid.country, mock_data['country'])
            self.assertEqual(humanoid.mobile, mock_data['mobile'])
            self.assertEqual(humanoid.name, mock_data['name'])
            self.assertEqual(humanoid.surname, mock_data['surname'])
            self.assertEqual(humanoid.phone, mock_data['phone'])
            self.assertEqual(humanoid.zip_code, int(mock_data['zip_code']))
            self.assertEqual(humanoid.img_url, '/static/profile_images/primary_img.jpg')
            self.assertEqual(humanoid.thumbnail_url, '/static/profile_images/thumbnail.jpg')

    @mock.patch(path_to_command + '.uuid.uuid1', return_value='imgmock')
    @mock.patch(path_to_command + '.requests.get')
    def test_image_creation(self, mocked_requests_get, mocket_uuid):
        mocked_requests_get.return_value.content = mock_image_in_bytes

        image_generator = HumanoidImagesGenerator()

        [img_filename, thumbnail_filename] = image_generator.create_humanoid_images()

        self.assertEqual(img_filename, 'imgmock_300.jpg')
        self.assertEqual(thumbnail_filename, 'imgmock_75.jpg')

        img_path = BASE_DIR / 'humanoids' / 'static' / 'profile_images' / img_filename
        thumbnail_path = BASE_DIR / 'humanoids' / 'static' / 'profile_images' / thumbnail_filename


        while not (img_path.exists() and thumbnail_path.exists()):
            time.sleep(1)
            print('checking image files creation...')

        self.assertTrue(img_path.is_file())
        self.assertTrue(thumbnail_path.is_file())

        img_path.unlink()
        thumbnail_path.unlink()

    @mock.patch(path_to_command + '.requests.get', side_effect=Exception('Connection error!'))
    def test_create_humanoid_images_connection_error(self, mocked_get):
        image_generator = HumanoidImagesGenerator()

        [img_filename, thumbnail_filename] = image_generator.create_humanoid_images()

        self.assertEqual(img_filename, 'placeholder300.jpg')
        self.assertEqual(thumbnail_filename, 'placeholder75.jpg')