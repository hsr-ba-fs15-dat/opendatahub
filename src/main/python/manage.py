#!/usr/bin/env python

""" Wrapper around django-admin to allow easier calling of commands. """

import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
