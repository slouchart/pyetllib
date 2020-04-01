from etllib.jobtools import Job


def my_func(msg, job_ref):
    job_ref.info(msg)


job = Job(name='foo', func=my_func, use_job=True)
result = job.run('OK')
