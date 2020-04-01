class BaseJobException(BaseException):
    ...


class JobAlreadyRegistered(BaseJobException, ValueError):
    ...


class JobReportNotFound(BaseJobException, KeyError):
    ...


class JobImportError(BaseJobException, ImportError):
    ...


class JobAttributeError(BaseJobException, AttributeError):
    ...


class JobNotCallable(BaseJobException, TypeError):
    ...


class BadJobRefError(BaseJobException, TypeError):
    ...
