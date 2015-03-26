
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models


class UserProfile(AbstractBaseUser):
    def get_short_name(self):
        pass

    def get_full_name(self):
        pass

    profile_photo = models.ImageField(upload_to='profiles')
    identifier = models.CharField(max_length=40, unique=True)
    username = models.CharField('username', max_length=30, unique=True,
                                help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                validators=[
                                    validators.RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.', 'invalid')
                                ])
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    email = models.EmailField('email address', blank=True)
    is_staff = models.BooleanField('staff status', default=False,
                                   help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True,
                                    help_text=('Designates whether this user should be treated as '
                                               'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
