from social.apps.django_app.default.models import UserSocialAuth

__author__ = 'remoliebi'
# from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class SocialUserInline(admin.StackedInline):
    model = UserSocialAuth
    can_delete = False
    verbose_name_plural = 'Weitere Details'


# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (SocialUserInline, )

# Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
