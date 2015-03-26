from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    # profile_photo = models.ImageField(
    # upload_to='profiles')  # for now we are just saving the direct url to the picture due to upload restrictuons
    profile_photo = models.TextField(default="")
    profile_photo_origin = models.CharField(max_length=30)
    description = models.TextField(default="")
