from unittest import TestCase, main as run_tests

import sys
import io
import os
import functools
import pathlib

from src.pyetllib.jobtools import Job
from src.pyetllib.jobtools import JobReport
from src.pyetllib.jobtools import get_report
import src.pyetllib.jobtools.exceptions as errors


def redirect_stdout(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _stdout = sys.stdout
        stream = io.StringIO()
        sys.stdout = stream
        args = (*args, stream)
        func(*args, **kwargs)
        sys.stdout = _stdout

    return wrapper


@Job.declare()
def noop_job():
    return "Done"


def dummy_job(_):
    Job.info('foo')
    return "OK"


@Job.declare()
def wrapped_job(_):
    Job.info('foo')
    return "OK"


@Job.declare()
def test_detach(_):
    Job.info('foo')
    return "OK"


class class_job(Job):
    def __run__(self, *args, **kwargs):
        self.info('foo')
        return "OK"


def some_func():
    return "Don't panic"


@Job.declare(use_job=True)
def with_job(job):
    job.info("OK")


class TestBasicJobExecution(TestCase):

    def test_cannot_call_directly_decorated_function(self):
        self.assertIsInstance(noop_job, Job)
        self.assertFalse(callable(noop_job))

    @redirect_stdout
    def test_job_exec(self, stdout):
        job = Job(func=dummy_job)
        result = job.execute('dummy_job', {}, module_name=__name__)
        self.assertIsInstance(result, JobReport)
        self.assertEqual(result.name, job.name)
        self.assertTrue(result.success)
        self.assertEqual(result.get_result(), "OK")
        self.assertTrue('foo' in stdout.getvalue())

    @redirect_stdout
    def test_job_exec_decorator(self, stdout):
        result = Job.execute('wrapped_job', {}, module_name=__name__,
                             stream=stdout)
        self.assertIsInstance(result, JobReport)
        self.assertEqual(result.name, 'wrapped_job')
        self.assertTrue(result.success)
        self.assertEqual(result.get_result(), "OK")
        self.assertTrue('foo' in stdout.getvalue())

    @redirect_stdout
    def test_job_instance(self, stdout):
        result = Job.execute('class_job', {}, module_name=__name__)
        self.assertIsInstance(result, JobReport)
        self.assertEqual(result.name, class_job.__name__)
        self.assertTrue(result.success)
        self.assertEqual(result.get_result(), "OK")
        self.assertTrue('foo' in stdout.getvalue())

    @redirect_stdout
    def test_detach_report(self, stdout):
        self.assertNotIn('test_detach', JobReport.reports)
        result = Job.execute('test_detach', {}, module_name=__name__,
                             stream=stdout)
        self.assertTrue(result.success)
        self.assertNotIn('test_detach', JobReport.reports)

    @redirect_stdout
    def test_job_makeover(self, _):
        job = Job(name='job42', func=some_func)
        result = Job.execute(job, color_output=False)
        self.assertTrue(result.success)
        self.assertIn("Don't panic", result.get_result())
        self.assertFalse(isinstance(some_func, Job))
        self.assertTrue(callable(some_func))

    @redirect_stdout
    def test_use_job(self, _):
        result = Job.execute('with_job', module_name=__name__)
        self.assertTrue(result.success)

    @redirect_stdout
    def test_as_subclass(self, _):
        result = Job.execute(class_job)
        self.assertTrue(result.success)


@Job.declare(logfile='testa.log')
def job_a(ctx):
    Job.info(f"foo {ctx['test']}")
    return True


class TestLogFile(TestCase):
    def setUp(self) -> None:
        io.open('testa.log', mode='w').close()
        io.open('testb.log', mode='w').close()

    @redirect_stdout
    def test_logfile_set_at_compile_time(self, stdout):
        Job.execute('job_a', {'test': 1}, module_name=__name__, stream=stdout)

        self.assertTrue(pathlib.Path('testa.log').exists())
        with io.open('testa.log', mode='r') as f:
            content = '\n'.join(f.readlines())
        self.assertIn('foo', content)

    @redirect_stdout
    def test_logfile_set_at_runtime(self, _):
        Job.execute('job_a', {'test': 2}, module_name=__name__,
                    logfile='testb.log')
        self.assertTrue(pathlib.Path('testb.log').exists())

        with io.open('testb.log', mode='r') as f:
            content = '\n'.join(f.readlines())
        self.assertIn('foo', content)

        with io.open('testa.log', mode='r') as f:
            content = '\n'.join(f.readlines())
        self.assertTrue(len(content) == 0)

    def tearDown(self) -> None:
        os.remove('testa.log')
        os.remove('testb.log')


@Job.declare()
def failing(_):
    raise ValueError("Oops!")


@Job.declare()
def failing_twice(_):
    Job.execute('failing', __name__, _)


class TestJobExceptionHandling(TestCase):
    @redirect_stdout
    def test_failing_job(self, stdout):
        result = Job.execute('failing', {}, module_name=__name__,
                             stream=stdout)
        self.assertIsInstance(result, JobReport)
        self.assertTrue(result.failure)
        self.assertEqual(str(result.get_result()), str(ValueError("Oops!")))

    @redirect_stdout
    def test_failing_twice(self, stdout):
        result = Job.execute('failing', {}, module_name=__name__,
                             stream=stdout)
        self.assertTrue(result.failure)
        self.assertEqual(str(result.get_result()), str(ValueError("Oops!")))


not_a_callable = ()


def dup_reports(job_name):
    def func():
        ...
    job = Job(job_name, func=func)
    job.run()


class TestJobDefinitionErrors(TestCase):

    def test_unregistered_job(self):
        with self.assertRaises(KeyError):
            _ = get_report('unknown')

    def test_no_a_callable(self):
        with self.assertRaises(TypeError) as cm:
            _ = Job.load('not_a_callable', __name__)
        self.assertEqual(str(cm.exception),
                         f"The object 'not_a_callable' in module '{__name__}' "
                         "does not resolve to a callable")

    def test_no_job(self):
        with self.assertRaises(AttributeError) as cm:
            _ = Job.load('___unknown', __name__)
        self.assertEqual(str(cm.exception),
                         f"Error loading job '___unknown', no job called "
                         f"'___unknown' in module '{__name__}'")

    def test_cannot_import(self):
        with self.assertRaises(ImportError) as cm:
            _ = Job.load('yada', '___unknown')
        self.assertEqual(str(cm.exception),
                         "Error loading job 'yada', could not import "
                         "module '___unknown'")

    @redirect_stdout
    def test_report_already_exists(self, _):
        job1 = Job(name='job', func=dup_reports)
        self.assertTrue(job1.name not in JobReport.reports)
        with self.assertRaises(errors.JobAlreadyRegistered):
            job1.run(job1.name)

        self.assertTrue(job1.name not in JobReport.reports)


@Job.declare(color_output=False, use_stream=True)
def no_color(ctx, stream):

    Job.info('Hello!')
    Job.execute('colored', __name__, ctx, color_output=True,
                stream=stream)


@Job.declare()
def colored(_):
    Job.info('Bye!')


class TestColorOutput(TestCase):

    @redirect_stdout
    def test_nocolor_output(self, stdout):
        result = Job.execute('no_color', {}, module_name=__name__,
                             stream=stdout)
        output = stdout.getvalue()
        self.assertIn(f'[no_color            ] {result.get_pid()} '
                      f'INFO                 Hello!',
                      output)

    @redirect_stdout
    def test_color_output(self, stdout):
        result = Job.execute('colored', {}, module_name=__name__,
                             stream=stdout)
        output = stdout.getvalue()
        self.assertNotIn(f'[colored             ] {result.get_pid()} '
                         f'INFO               Bye!',
                         output)
        self.assertIn('colored', output)
        self.assertIn('Bye!', output)


if __name__ == '__main__':
    run_tests(verbosity=2)
