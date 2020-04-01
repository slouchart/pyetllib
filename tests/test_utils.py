from unittest import TestCase
from unittest import main as run_tests
from time import sleep

from src.pyetllib.etllib.utils import log_timed_statistics


def func():
    """Some help"""
    sleep(1)


class TestLogTimedStatistics(TestCase):
    def setUp(self) -> None:
        self.logger_name = "test_utils"
        self.timed_function = log_timed_statistics(
            logger_name=self.logger_name)(func)

    def test_decoration(self):
        self.assertEqual(self.timed_function.__name__, func.__name__)
        self.assertEqual(self.timed_function.__doc__, func.__doc__)
        self.assertTrue(callable(self.timed_function))

    def test_correct_logging(self):
        with self.assertLogs(logger=self.logger_name, level='INFO') as cm:
            self.timed_function()
        self.assertGreater(len(cm.output), 0)
        self.assertIn(f'INFO:{self.logger_name}:time elapsed (seconds)',
                      cm.output[0])


if __name__ == "__main__":
    run_tests(verbosity=2)
