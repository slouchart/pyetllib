from pyetllib.jobtools import Job


class ColoredOutput(Job):

    def __run__(self, *args, **kwargs):
        self.info("OK")


Job.execute(ColoredOutput)