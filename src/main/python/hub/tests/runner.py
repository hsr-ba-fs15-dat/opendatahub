from django.test.runner import DiscoverRunner

from hub.management.commands.loadfixtures import Command as LoadFixtures


class ParameterizedTestRunner(DiscoverRunner):
    def load_fixtures(self):
        print 'Loading fixtures'
        LoadFixtures(parse=False).handle()

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        self.setup_test_environment()
        old_config = self.setup_databases()

        self.load_fixtures()

        suite = self.build_suite(test_labels, extra_tests)
        result = self.run_suite(suite)

        self.teardown_databases(old_config)
        self.teardown_test_environment()

        return self.suite_result(suite, result)
