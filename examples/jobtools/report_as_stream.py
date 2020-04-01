from etllib.jobtools import Job
import io


@Job.declare(use_stream=True, color_output=False)
def streamer(stream):
    stream.write('yada\n')
    Job.info("OK")


s = io.StringIO()
Job.execute(streamer, stream=s)
print(s.getvalue())
