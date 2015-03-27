import urlparse
from abc import abstractmethod
from social.backends.github import GithubOAuth2

from social.backends.open_id import OpenIdAuth
from social.exceptions import AuthMissingParameter


class LiveJournalOpenId(OpenIdAuth):
    """LiveJournal OpenID authentication backend"""
    name = 'livejournal'

    def get_user_details(self, response):
        """Generate username from identity url"""
        values = super(LiveJournalOpenId, self).get_user_details(response)
        values['username'] = values.get('username') or urlparse.urlsplit(response.identity_url).netloc.split('.', 1)[0]
        return values

    def openid_url(self):
        """Returns LiveJournal authentication URL"""
        if not self.data.get('openid_lj_user'):
            raise AuthMissingParameter(self, 'openid_lj_user')
        return 'http://%s.livejournal.com' % self.data['openid_lj_user']


class OdhGithubOAuth2(GithubOAuth2):
    @abstractmethod
    def auth_html(self):
        return

    def get_user_id(self, details, response):
        return response.get('login')