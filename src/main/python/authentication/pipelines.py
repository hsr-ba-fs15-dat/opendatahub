from requests import request, HTTPError


def save_profile_picture(strategy, user, response, details, is_new=False, *args, **kwargs):
    if is_new or True:
        url = None
        if strategy.request.backend.name == 'facebook':
            url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])
        if strategy.request.backend.name == 'github':
            url = response[u'avatar_url']

        try:
            response = request('GET', url, params={'type': 'large'})
            response.raise_for_status()
        except HTTPError:
            pass
        else:

            # profile.profile_photo.save('{0}_social.jpg'.format(user.username), ContentFile(response.content))
            user.profile_photo = url
            user.profile_photo_origin = strategy.request.backend.name
            user.save()
