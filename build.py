"""
PyBuilder configuration file
"""

from pybuilder.core import use_plugin, after, init, task, description
from pybuilder.utils import assert_can_execute
from pybuilder.errors import BuildFailedException
from pybuilder.pluginhelper.external_command import ExternalCommandBuilder


use_plugin("analysis")
use_plugin('python.core')
use_plugin('python.unittest')
use_plugin('python.coverage')
use_plugin('python.flake8')
use_plugin('python.install_dependencies')
use_plugin('pypi:pybuilder_django_enhanced_plugin')

default_task = ['install_dependencies', 'django_makemigrations', 'django_migrate', 'analyze', 'publish']

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



@task
@description("Runs django dbshell")
def django_dbshell(project, logger):
    from pybuilder_django_enhanced_plugin.tasks.common import get_django_command_args
    from django.core.management import execute_from_command_line

    args = ['dbshell']
    args += get_django_command_args(project)
    logger.info("Running django dbshell {} ".format(args))
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
