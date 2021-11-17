from django.db import models

class Humanoid(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    bio = models.TextField(max_length=2500)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    zip_code = models.IntegerField(default=0)
    img_url = models.URLField()
    thumbnail_url = models.URLField()

    def __str__(self) -> str:
        return self.name

    @property
    def full_name_list(self):
        return f'{self.name.lower()} {self.surname.lower()}'.split()


