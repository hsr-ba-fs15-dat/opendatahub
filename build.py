"""
PyBuilder configuration file
"""

from pybuilder.core import use_plugin, after, init, task, description, depends
from pybuilder.utils import assert_can_execute, execute_command, read_file
from pybuilder.plugins.python.python_plugin_helper import log_report
from pybuilder.errors import BuildFailedException
from pybuilder.pluginhelper.external_command import ExternalCommandBuilder


import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WEBAPP_DIR = os.path.join(BASE_DIR, 'src', 'main', 'webapp')


use_plugin("analysis")
use_plugin('python.core')
use_plugin('python.unittest')
use_plugin('python.coverage')
use_plugin('python.flake8')
use_plugin('python.install_dependencies')
use_plugin('pypi:pybuilder_django_enhanced_plugin')

default_task = ['clean', 'install_dependencies', 'django_makemigrations', 'django_migrate', 'django_test', 'grunt', 'analyze', 'publish']

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
    project.set_property('flake8_ignore', 'F401,E501,E128')
    project.set_property('flake8_max_line_length', 160)




def custom_exec(project, logger, args, name=None, cwd=None, fail_error=True):
    cmd = args[0]
    name = name or cmd
    logger.debug('Checking availability of ' + cmd)
    assert_can_execute((cmd,), cmd, 'plugin opendatahub.' + name)
    logger.debug(name + ' has been found')

    report_file = project.expand_path('$dir_reports/{0}'.format('bower'))
    error_report_file = '{0}.err'.format(report_file)

    logger.info('Running {}'.format(args))
    exit_code = execute_command(args, report_file, cwd=cwd)
    report_lines = read_file(report_file)
    error_report_lines = read_file(error_report_file)

    verbose = project.get_property('verbose')
    if error_report_lines:
        msg = 'Errors while running {0}, see {1}'.format(name, error_report_file)
        if verbose:
            logger.info(''.join(error_report_lines))
        if fail_error:
            raise BuildFailedException(msg)

    if verbose:
        logger.info(''.join(report_lines))



@task('install_runtime_dependencies')
def install_bower_packages(project, logger):
    custom_exec(project, logger, ['bower', 'install', '--config.analytics=false', '--allow-root', '--no-interactive'], cwd=WEBAPP_DIR)


@task('install_build_dependencies')
def install_npm_packages(project, logger):
    custom_exec(project, logger, ['npm', 'install'], cwd=WEBAPP_DIR, fail_error=False)


@task
@depends('install_build_dependencies','install_runtime_dependencies')
@after(('run_unit_tests',), only_once=True)
def grunt(project, logger):
    custom_exec(project, logger, ['grunt'], cwd=WEBAPP_DIR, fail_error=True)


@task('django_migrate')
def django_migrate_fix(project, logger):
    from pybuilder_django_enhanced_plugin.tasks.common import run_django_manage_command

    args = ['migrate']
    command_result = run_django_manage_command(project, logger, 'django_migrate', args)
    if command_result.exit_code != 0:
        error_message = ''.join(command_result.error_report_lines)
        logger.error('Django migrate failed: {}'.format(error_message))
        raise BuildFailedException('Django migrate failed')
    return command_result


@task
def django_flush(project, logger):
    from pybuilder_django_enhanced_plugin.tasks.common import run_django_manage_command

    args = ['flush', '--noinput']
    command_result = run_django_manage_command(project, logger, 'django_flush', args)
    if command_result.exit_code != 0:
        error_message = ''.join(command_result.error_report_lines)
        logger.error('Django flush failed: {}'.format(error_message))
        raise BuildFailedException('Django flush failed')
    return command_result


@task
@description('Runs django dbshell')
def django_dbshell(project, logger):
    from pybuilder_django_enhanced_plugin.tasks.common import get_django_command_args
    from django.core.management import execute_from_command_line

    args = ['dbshell']
    args += get_django_command_args(project)
    logger.info('Running django dbshell {} '.format(args))
    execute_from_command_line([''] + args)

@task
def dbshell(project, logger):
    django_dbshell(project, logger)

@init
def init_pylint(project):
    project.build_depends_on('pylint')

@after('prepare')
def check_pylint_availability(logger):
    logger.debug('Checking availability of pylint')
    assert_can_execute(('pylint', ), 'pylint', 'plugin python.pylint')
    logger.debug('pylint has been found')

@task('analyze')
def execute_pylint(project, logger):
    logger.info('Executing pylint on project sources')
    verbose = project.get_property('verbose')

    command = ExternalCommandBuilder('pylint', project)
    command.use_argument('--msg-template="{C}:{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"')
    result = command.run_on_production_source_files(logger, include_test_sources=True, include_scripts=True)

    if result.error_report_lines:
        msg = 'Errors while running pylint, see {0}'.format(result.error_report_file)
        if verbose:
            logger.info(''.join(result.error_report_lines))
        raise BuildFailedException(msg)

    if verbose:
        logger.info(''.join(result.report_lines))

    breaking_warnings = [l for l in result.report_lines if l.startswith('E:') or l.startswith('F:')]
    if breaking_warnings:
        raise BuildFailedException(''.join(breaking_warnings))
