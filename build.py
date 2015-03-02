"""
PyBuilder configuration file
"""

from pybuilder.core import use_plugin, init

use_plugin('python.core')
use_plugin('python.unittest')
use_plugin('python.flake8')
use_plugin('python.install_dependencies')
use_plugin('pypi:pybuilder_django_enhanced_plugin')

default_task = ['install_dependencies', 'analyze', 'publish']


@init
def initialize(project):
    project.depends_on_requirements('requirements.txt')
    project.build_depends_on_requirements('requirements_dev.txt')
    project.set_property('install_dependencies_upgrade', True)

    project.set_property('django_project', 'opendatahub')
    project.set_property('django_apps', ['home'])


    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_break_build', True)

    # F401: Unused import
    # E501: long time
    # E128: visual indent
    project.set_property('flake8_ignore', 'F401,E501,E128')
    project.set_property('flake8_max_line_length', 160)
