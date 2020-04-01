import time

from pyetllib.jobtools import Job


def sleepy(idle):
    time.sleep(idle)


job = Job(func=sleepy)
job.run(60)  # expected elapsed 60.0
job.run(15.8754)  # expected elapsed 15.88
