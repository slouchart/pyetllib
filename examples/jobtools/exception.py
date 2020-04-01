from pyetllib.jobtools import Job


@Job.declare()
def failing():
    Job.error('KO')
    raise RuntimeError("I haven't been caught")


Job.execute(failing)
