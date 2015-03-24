import os

__author__ = 'remoliebi'
FACEBOOK_SECRET = os.environ.get('FACEBOOK_SECRET') or 'Facebook Client Secret'
GITHUB_SECRET = os.environ.get('GITHUB_SECRET') or 'GitHub Client Secret'
FOURSQUARE_SECRET = os.environ.get('FOURSQUARE_SECRET') or 'Foursquare Client Secret'
GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET') or 'Google Client Secret'
LINKEDIN_SECRET = os.environ.get('LINKEDIN_SECRET') or 'LinkedIn Client Secret'
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY') or 'Twitter Consumer Secret'
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET') or 'Twitter Consumer Secret'
TWITTER_CALLBACK_URL = os.environ.get('TWITTER_CALLBACK_URL') or 'Twitter Redirect URI'

FACEBOOK_PUBLIC = os.environ.get('FACEBOOK_PUBLIC') or '401522313351953'
GITHUB_PUBLIC = os.environ.get('GITHUB_PUBLIC') or 'f29d882c342818c82e0b'
