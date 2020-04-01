from pyetllib.jobtools import Job


@Job.declare()
def colored_output():
    Job.info('OK')


Job.execute(colored_output)

