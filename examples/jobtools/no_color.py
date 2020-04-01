from pyetllib.jobtools import Job


@Job.declare(color_output=False)
def no_color():
    Job.info('OK')


Job.execute(no_color)

