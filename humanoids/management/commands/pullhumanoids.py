from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import requests
from PIL import Image
from io import BytesIO
from core.settings import FAKE_JSON_TOKEN
from humanoids.models import Humanoid
import uuid


def fetch_humanoids_data():
    payload = {
        "token": FAKE_JSON_TOKEN,
        "data": {
            "name": "nameFirst",
            "surname": "nameLast",
            "address": "addressFullStreet",
            "zip_code": "addressZipCode",
            "city": "addressCity",
            "country": "addressState",
            "phone": "phoneHome",
            "mobile": "phoneMobile",
            "email": "internetEmail",
            "bio": "stringLong",
            "_repeat": 10
        }
    }
    try:
        response = requests.post("https://app.fakejson.com/q", json=payload)

        return response.json()
    except:
        print('unable to fetch humanoids data')
        return None


def to_img_url(filename):
    return  f'https://humanoidspictures.s3.eu-south-1.amazonaws.com/{filename}'


class HumanoidImagesGenerator:
    last_content = None 

    def create_humanoid_images(self):
        sizes = [300, 75]
        try:
            img_content = None

            while(img_content == None or img_content == self.last_content):
                img_response = requests.get('https://thispersondoesnotexist.com/image')
                img_content = img_response.content

            self.last_content = img_content

            result_filenames = []

            img_id =  str(uuid.uuid1())
            img = Image.open(BytesIO(img_response.content))

            for size in sizes:
                memfile = BytesIO()
                img.thumbnail((size, size))
                filename = f'{img_id}_{size}.jpg'
                img.save(memfile, 'JPEG')
                default_storage.save(filename, memfile)
                result_filenames.append(filename)
                memfile.close()
            
            img.close()

            return result_filenames        
        except:

            result_filenames = []
            for size in sizes:
                filename = 'placeholder' + str(size) + '.jpg'
                result_filenames.append(filename)
            
            return result_filenames



class Command(BaseCommand):
    help = 'Pull new humanoids and store them in the database'

    def handle(self, *args, **options):

        all_humanoids_data = fetch_humanoids_data()

        if not all_humanoids_data:
            return

        images_generator = HumanoidImagesGenerator()

        for humanoid_data in all_humanoids_data:
            if not Humanoid.objects.filter(email=humanoid_data['email']).exists():
                new_humanoid = Humanoid(**humanoid_data)

                [img_filename, thumbnail_filename] = images_generator.create_humanoid_images()

                new_humanoid.img_url = to_img_url(img_filename)
                new_humanoid.thumbnail_url = to_img_url(thumbnail_filename)

                new_humanoid.save()