# -*- coding: utf-8 -*-

"""
PyBuilder configuration file
"""

import shutil
import itertools

from pybuilder.core import use_plugin, after, init, task, depends
from pybuilder.utils import assert_can_execute, execute_command, read_file
from pybuilder.errors import BuildFailedException
from pybuilder.pluginhelper.external_command import ExternalCommandBuilder
import os
import fnmatch


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WEBAPP_DIR = os.path.join(BASE_DIR, 'src', 'main', 'webapp')
DJANGO_DIR = os.path.join(BASE_DIR, 'src', 'main', 'python')

use_plugin('analysis')
use_plugin('python.core')
use_plugin('python.unittest')
# use_plugin('python.coverage')  # disabled as it doesn't work out of the box with django tests anyway
use_plugin('python.flake8')
use_plugin('python.install_dependencies')
# use_plugin('pypi:pybuilder_django_enhanced_plugin')

default_task = ['clean', 'install_dependencies', 'django_makemigrations', 'django_migrate', 'django_createcachetable',
                'django_test', 'grunt', 'analyze', 'publish']


@init
def initialize(project):
    project.set_property('install_dependencies_upgrade', True)
    project.depends_on_requirements('requirements.txt')
    project.build_depends_on_requirements('requirements_dev.txt')

    project.set_property('django_project', 'opendatahub')
    project.set_property('django_apps', ['hub'])

    project.set_property('coverage_break_build', False)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_break_build', True)
    project.set_property('flake8_verbose_output', True)

    # F401: Unused import
    # E501: long line
    # E128: visual indent
    project.set_property('flake8_ignore', 'E128')
    project.set_property('flake8_max_line_length', 120)
    project.set_property('flake8_exclude_patterns', '0001_*.py')
    project.set_property('pylint_fail_on_ids', [
        'E*',
        'F*',
        'C0103',  # invalid-name
        'W0403'  # relative-import
    ])


def custom_exec(project, logger, args, name=None, cwd=None, fail_stderr=True, fail_nonzero=True):
    cmd = args[0]
    name = name or cmd
    logger.debug('Checking availability of ' + cmd)
    assert_can_execute((cmd,), cmd, 'plugin opendatahub.' + name)
    logger.debug(name + ' has been found')

    report_file = project.expand_path('$dir_reports/{0}'.format(name))
    error_report_file = '{0}.err'.format(report_file)

    logger.info('Running {}'.format(args))
    exit_code = execute_command(args, report_file, cwd=cwd)
    report_lines = read_file(report_file)
    error_report_lines = read_file(error_report_file)

    verbose = project.get_property('verbose')
    if verbose:
        logger.info(''.join(report_lines))

    if error_report_lines or exit_code != 0:
        msg = 'Errors while running {0}, see {1}'.format(name, error_report_file)
        if verbose:
            logger.info(''.join(error_report_lines))
        if (error_report_lines and fail_stderr) or (exit_code != 0 and fail_nonzero):
            raise BuildFailedException(msg)


def django_exec(project, logger, args, **kwargs):
    django_project = project.get_property('django_project')
    django_apps = project.get_property('django_apps')
    args_ex = ['--settings={}.settings'.format(django_project), '--pythonpath=' + DJANGO_DIR]
    return custom_exec(project, logger, ['django-admin'] + args + args_ex, **kwargs)


@task('install_runtime_dependencies')
def install_bower_packages(project, logger):
    custom_exec(project, logger, ['bower', 'install', '--config.analytics=false', '--allow-root', '--no-interactive'],
                cwd=WEBAPP_DIR, fail_stderr=False)


@task('install_build_dependencies')
def install_npm_packages(project, logger):
    custom_exec(project, logger, ['npm', 'install'], cwd=WEBAPP_DIR, fail_stderr=False)


@task('install_build_dependencies')
def install_typings(project, logger):
    shutil.rmtree(os.path.join(WEBAPP_DIR, 'typings'), ignore_errors=True)
    custom_exec(project, logger, ['tsd', 'reinstall'], cwd=WEBAPP_DIR)
    custom_exec(project, logger, ['tsd', 'rebundle'], cwd=WEBAPP_DIR)


@task
@depends('install_build_dependencies', 'install_runtime_dependencies')
@after(('run_unit_tests',), only_once=True)
def grunt(project, logger):
    custom_exec(project, logger, ['grunt'], cwd=WEBAPP_DIR)


@task
@depends('prepare')
def django_test(project, logger):
    django_exec(project, logger, ['test', '--noinput', '--failfast'] + project.get_property('django_apps'), fail_stderr=False)


@task
@depends('prepare')
def django_makemigrations(project, logger):
    django_exec(project, logger, ['makemigrations', '--noinput'], fail_stderr=False)


@task
@depends('prepare')
def django_migrate(project, logger):
    django_exec(project, logger, ['migrate', '--noinput'], fail_stderr=False)


@task
@depends('prepare')
def django_collectstatic(project, logger):
    django_exec(project, logger, ['collectstatic', '--noinput'], fail_stderr=False)


@task
@depends('prepare')
def django_loadfixtures(project, logger):
    django_exec(project, logger, ['loadfixtures'], fail_stderr=False)


@task
@depends('prepare')
def django_createcachetable(project, logger):
    django_exec(project, logger, ['createcachetable'], fail_stderr=False)


@task
@depends('prepare')
def django_flush(project, logger):
    django_exec(project, logger, ['flush', '--noinput'], fail_stderr=False)


@task
@depends('prepare')
def django_reset_db(project, logger):
    django_exec(project, logger, ['reset_db', '--noinput'], fail_stderr=False)
    django_createcachetable(project, logger)


@task
@depends('prepare')
def django_init_db(project, logger):
    django_reset_db(project, logger)
    django_makemigrations(project, logger)
    django_migrate(project, logger)
    django_createcachetable(project, logger)
    django_loadfixtures(project, logger)


@init
def init_pylint(project):
    project.build_depends_on('pylint')


@after('prepare')
def check_pylint_availability(logger):
    logger.debug('Checking availability of pylint')
    assert_can_execute(('pylint', ), 'pylint', 'plugin python.pylint')
    logger.debug('pylint has been found')


@task('analyze')
@depends('prepare')
def execute_pylint(project, logger):
    logger.info('Executing pylint on project sources')
    verbose = project.get_property('verbose')
    failure_ids = project.get_property('pylint_fail_on_ids', [])

    command = ExternalCommandBuilder('pylint', project)
    command.use_argument('--msg-template="{msg_id}({symbol}):{path}:{line}:{obj}:{msg}"')
    result = command.run_on_production_source_files(logger, include_test_sources=True, include_scripts=True)

    if result.error_report_lines:
        msg = 'Errors while running pylint, see {0}'.format(result.error_report_file)
        if verbose:
            logger.info(''.join(result.error_report_lines))
        raise BuildFailedException(msg)

    if verbose:
        logger.info(''.join(result.report_lines))

    breaking_lines = list(
        itertools.chain(*[fnmatch.filter(result.report_lines, pattern + '(*') for pattern in failure_ids]))
    if breaking_lines:
        raise BuildFailedException(''.join(breaking_lines))
