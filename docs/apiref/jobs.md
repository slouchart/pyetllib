# `etllib.jobtools` — job management and reporting
---

## class `Job`
`Job(self, name=None, func=None, use_job=False, use_stream=False, color_output=True, logfile=None)`
creates a job to be executed later. Some instance properties can be
initialized at creation. `name` represent the identity of the job and
must be unique across your application. `func` is any regular callable
the job will execute when told to do so with the `run` method.

`use_job` and `use_stream` are flags that instruct the job to provide
the inner `func` with specific arguments at runtime. If `use_job` is set
to `True`, the first argument passed to `func`is a reference to the `Job`.
If `use_stream` is set to `True`, the second (or the first) argument
passed to `func` is the job current output stream which can be `sys.stdout`.
 
`colour_output` instructs the underlying `JobReport` instance of the job to use
ANSI escape sequences when logging to the standard output.

`logfile` is a path-like object used to associate the `JobReport` instance of 
the job to a logging file using `logging.FileHandler`.

### properties

`name` a string-like object identifying the job

`func` the callable passed as an argument at instance creation or the decorated function returned by `Job.declare`

`color_output` flag indicating whether or not to use ANSI escape sequences 
to color the `JobReport` output

`logfile` path-like object representing the location of the job's logging file

`stream` stream object (like `io.StringIO`) representing the current output of the job


### methods
`declare(cls, name=None, use_job=False, use_stream=False, color_output=True, logfile=None)`
is a decorator function that turns the function it decorates into a instance of `Job` created
using its own arguments. The arguments have thus the same meaning as their 
counter part in `Job.__init__`.

`load_from_pkg(cls, job_name, module_name)` 

`load(cls, job_ref, module_name='')`

`execute(cls, job_ref, *args, module_name='', color_output=None, logfile=None, stream=None, **kwargs)`

`prepare(self, color_output, logfile, stream)`

`run(self, *args, color_output=None, logfile=None, stream=None, **kwargs)`

`__prologue__(self)`

`__epilogue__(self, success: bool)`

`__run__(self, *args, **kwargs)`

`reset_color_output(self, value)`

`reset_logfile(self, value)`

`reset_stream(self, value)`

`info(msg)`

`debug(msg)`

`error(msg)`

`warning(msg)`

`ok(msg)`

`fail(msg)`

`prologue(msg)`

`epilogue(msg)`

## class `JobReport`
`JobReport(self, job_name, color_output=True, logfile=None, stream=None)`

### properties
`name`

`success`

`failure`


### methods

`set_result(self, result)`


`get_result(self)`


`set_pid(self, pid)`


`get_pid(self)`
 

`finalize(self)`


`get_report(cls, name)`

`detach(cls, report)`

`register(cls, job_name, color_output=True, logfile=None, stream=None, force=False)`

`report(self, level, msg, *args, **kwargs)`

`info(self, msg)`

`debug(self, msg)`

`error(self, msg)`

`warning(self, msg)`

`ok(self, msg)`

`fail(self, msg)`

`prologue(self, msg)`

`epilogue(self, msg)`

## function `get_report`
`get_report(name)`

## exceptions

`BaseJobException`

`JobAlreadyRegistered`
 subclass of `ValueError`



`JobReportNotFound`
subclass of `KeyError`


`JobImportError`
 subclass of `ImportError`

`JobAttributeError`
subclass of `AttributeError`

`JobNotCallable`
subclass of  `TypeError`

`BadJobRefError`
subclass of `TypeError`
   
