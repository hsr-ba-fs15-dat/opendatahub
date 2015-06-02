"""
Authentication config for opendatahub project.
It contains the public and secret keys for authentication of different used social networks
"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

FACEBOOK_SECRET = os.environ.get('FACEBOOK_SECRET') or 'Facebook Client Secret'
GITHUB_SECRET = os.environ.get('GITHUB_SECRET') or 'GitHub Client Secret'
FOURSQUARE_SECRET = os.environ.get('FOURSQUARE_SECRET') or 'Foursquare Client Secret'
GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET') or 'Google Client Secret'
LINKEDIN_SECRET = os.environ.get('LINKEDIN_SECRET') or 'LinkedIn Client Secret'
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY') or 'Twitter Consumer Secret'
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET') or 'Twitter Consumer Secret'
TWITTER_CALLBACK_URL = os.environ.get('TWITTER_CALLBACK_URL') or 'Twitter Redirect URI'
SOCIAL_AUTH_FACEBOOK_SECRET = FACEBOOK_SECRET
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('FACEBOOK_PUBLIC', '401522313351953')
FACEBOOK_PUBLIC = os.environ.get('FACEBOOK_PUBLIC', '401522313351953')
GITHUB_PUBLIC = os.environ.get('GITHUB_PUBLIC', 'b24753ec88ca98150354')
SOCIAL_AUTH_GITHUB_KEY = GITHUB_PUBLIC
SOCIAL_AUTH_GITHUB_SECRET = GITHUB_SECRET
