import sys
import logging
from functools import wraps
from StringIO import StringIO

class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.messages = {}
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

class MockStringIO(StringIO):
    """ It implements the context management methods to support open using
    with statement.

    NOTE: the "StringIO" class from the module "io" has support for context
    management, however it wasn't possible to use in our tests as it is
    not compatible with the "csv" library while trying to write data, giving
    errors like: "TypeError: can't write str to text stream". The old
    "StringIO" version from the "StringIO" module works fine, despite the
    problem with the context management. That's why this class patch has been
    implemented, to be possible to use in our tests.
    """

    def __enter__(self):
        """ Context management protocol. Returns self.
        """
        return self

    def __exit__(self, *args):
        """ Context management protocol. Calls close().
        """
        buf = getattr(self, 'buf', '')
        if not self.buflist and buf:
            self.buflist = ["%s\n" % i for i in buf.splitlines()]
        self.close()

def mock_stdout(func):
        """ Decorator to mock standard outputs or errors.
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self._original_stdout = sys.stdout
            self._original_stderr = sys.stderr
            self._mock_stdout = MockStringIO()
            self._mock_stderr = MockStringIO()
            sys.stdout = self._mock_stdout
            sys.stderr = self._mock_stderr
            ret_val = func(self, *args, **kwargs)
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            return ret_val
        return wrapper