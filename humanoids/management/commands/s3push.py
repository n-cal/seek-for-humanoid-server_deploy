from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from PIL import Image
from io import BytesIO
import uuid
from pathlib import Path


class Command(BaseCommand):

  def handle(self, *args, **options):
    img_id = uuid.uuid1()
    img = Image.open('placeholder300.jpg')

    memfile = BytesIO()
    img.save(memfile, 'JPEG')
    default_storage.save('placeholder300.jpg', memfile)
    memfile.close()
    img.close()