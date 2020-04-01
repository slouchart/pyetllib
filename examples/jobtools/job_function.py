from pyetllib.jobtools import Job


def job(job_ref):
    job_ref.info('OK')


job = Job(func=job, use_job=True)
Job.execute(job)
