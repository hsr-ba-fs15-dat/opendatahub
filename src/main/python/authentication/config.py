"""
Authentication config for opendatahub project.
It contains the public and secret keys for authentication of different used social networks
"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from opendatahub.settings import PRODUCTION


FACEBOOK_SECRET = os.environ.get('FACEBOOK_SECRET') or 'Facebook Client Secret'
GITHUB_SECRET = os.environ.get('GITHUB_SECRET') or 'GitHub Client Secret'
FOURSQUARE_SECRET = os.environ.get('FOURSQUARE_SECRET') or 'Foursquare Client Secret'
GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET') or 'Google Client Secret'
LINKEDIN_SECRET = os.environ.get('LINKEDIN_SECRET') or 'LinkedIn Client Secret'
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY') or 'Twitter Consumer Secret'
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET') or 'Twitter Consumer Secret'
TWITTER_CALLBACK_URL = os.environ.get('TWITTER_CALLBACK_URL') or 'Twitter Redirect URI'

FACEBOOK_PUBLIC = '401520096685508' if PRODUCTION else os.environ.get('FACEBOOK_PUBLIC', '401522313351953')
GITHUB_PUBLIC = '8ef558ed3fb0f5385da5' if PRODUCTION else os.environ.get('GITHUB_PUBLIC', 'b24753ec88ca98150354')
