# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import abstractmethod
from social.backends.github import GithubOAuth2


class OdhGithubOAuth2(GithubOAuth2):
    @abstractmethod
    def auth_html(self):
        return
