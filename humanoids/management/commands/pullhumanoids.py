from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import requests
from PIL import Image
from io import BytesIO
from core.settings import FAKE_JSON_TOKEN, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME
from humanoids.models import Humanoid
import uuid

HUMANOIDS_PER_REQUEST = 10

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
            "_repeat": HUMANOIDS_PER_REQUEST
        }
    }
    try:
        response = requests.post("https://app.fakejson.com/q", json=payload)

        return response.json()
    except:
        print('unable to fetch humanoids data')
        return None


def to_img_url(filename):
    return  f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{filename}'


class HumanoidImagesGenerator:
    # need a variable here because fetching images too fast from thispersondoesnotexists.com
    # often will give the same result. 
    last_content = None 

    def create_humanoid_images(self):
        sizes = [300, 75]
        try:
            # try to fetch until we have a new result
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
            print('ERROR: generating humanoid images -> setting images to placeholders.')
            result_filenames = []
            for size in sizes:
                filename = 'placeholder' + str(size) + '.jpg'
                result_filenames.append(filename)
            
            return result_filenames



class Command(BaseCommand):
    help = 'Pull new humanoids and store them in the database'

    def handle(self, *args, **options):

        print('fetching humanoids data...')
        all_humanoids_data = fetch_humanoids_data()

        if not all_humanoids_data:
            print('ERROR: fetching humanoids data')
            return

        images_generator = HumanoidImagesGenerator()

        created_humanoids_count = 0

        for humanoid_data in all_humanoids_data:
            if not Humanoid.objects.filter(email=humanoid_data['email']).exists():
                new_humanoid = Humanoid(**humanoid_data)

                print(f'creating images for humanoid {created_humanoids_count + 1}/{HUMANOIDS_PER_REQUEST}...')
                [img_filename, thumbnail_filename] = images_generator.create_humanoid_images()

                new_humanoid.img_url = to_img_url(img_filename)
                new_humanoid.thumbnail_url = to_img_url(thumbnail_filename)

                new_humanoid.save()
                created_humanoids_count += 1
                print(f'humanoids {created_humanoids_count}/{HUMANOIDS_PER_REQUEST} saved.')
        
        print(f'{HUMANOIDS_PER_REQUEST - created_humanoids_count} humanoids already in database, run this command later.')
        print(f'Created {created_humanoids_count}/{HUMANOIDS_PER_REQUEST} humanoids.')