# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    """
    Model for the Users Profile. Extends AbstractUser for addition of Social Media Picture and a description.
    (Currently not used entirely)
    """
    profile_photo = models.TextField(default="")
    profile_photo_origin = models.CharField(max_length=30)
    description = models.TextField(default="")
