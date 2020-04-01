from pyetllib.jobtools import Job
from pathlib import Path
import os
import io
import sys


@Job.declare()
def to_log():
    Job.info("OK")


logfile = Path('temp.log')
if logfile.exists():
    os.remove(logfile)

Job.execute(to_log, logfile=logfile)

print("File content:")
with io.open(logfile, mode='r') as f:
    for line in f:
        sys.stdout.write(line)

os.remove(logfile)