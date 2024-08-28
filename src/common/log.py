####################################################################
# COPYRIGHT Ericsson AB 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
####################################################################
from __future__ import print_function
import sys

from logging import getLogger, DEBUG, Formatter, FileHandler
from logging.handlers import SysLogHandler
import os.path


class NRNSALogger(object):
    """ This class abstracts all the logging and standard output printing
    methods used for NRNSA.
    """

    logger = None
    format = 'NR-NSA %(levelname)s: %(message)s'
    file_format = '%(asctime)s ' + format
    date_format = '%b %d %H:%M:%S'
    bars = ["-", "\\", "|", "/"]

    class Settings(object):
        """ These settings here are for the user CLI.
        """
        verbose = False

    @classmethod
    def setup_log(cls):
        """ It setups the logger just once in an execution using a FileHandler.
        """
        if NRNSALogger.logger is not None:
            # setup only once...
            return
        NRNSALogger.logger = getLogger(__name__)
        cls.logger.setLevel(DEBUG)
        cls.create_handlers()

    @classmethod
    def create_handlers(cls):
        """ It setups the logger just once in an execution using a FileHandler.
        """
        log_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../log/nrnsa_log")
        sys_handler = SysLogHandler("/dev/log")
        file_handler = FileHandler(log_path, 'w')
        sys_formatter = Formatter(cls.format)
        file_formatter = Formatter(cls.file_format, cls.date_format)
        cls.setup_handler(sys_handler, sys_formatter)
        cls.setup_handler(file_handler, file_formatter)

    @classmethod
    def setup_handler(cls, handler, formatter):
        """ It setups the handler with level and format.
        """
        handler.setLevel(DEBUG)
        handler.setFormatter(formatter)
        cls.logger.addHandler(handler)

    @classmethod
    def prints(cls, message, only_when_verbose=False):
        """ In case verbose mode is True, it prints the message.
        """
        if only_when_verbose and cls.Settings.verbose or not only_when_verbose:
            print(message)

    @classmethod
    def print_flush(cls, message, only_when_verbose=False):
        """ Writes a message in stdout and flush to keep in the same line.
        """
        if only_when_verbose and cls.Settings.verbose or not only_when_verbose:
            sys.stdout.write(message)
            sys.stdout.flush()

    @classmethod
    def progress(cls, prefix, percentage):
        """ Prints a progress percentage given a percentage number.
        """
        if int(percentage) == 100:
            progress_bar = ""  # u"\u221A".encode('utf-8')
        else:
            progress_bar = cls.bars.pop(0)
        if cls.Settings.verbose:
            # ignore rotating bar when verbose mode is on.
            progress_bar = "-"
        cls.bars.append(progress_bar)
        cls.print_flush(u"\r%s: %s%% %s " % (prefix, percentage, progress_bar))

    def info(self, msg):
        """ It uses the logger to log as info and also print in case verbose
        mode is True.
        """
        self.logger.info(msg)
        self.prints(msg, only_when_verbose=True)

    def warn(self, msg):
        """ It uses the logger to log as warn and also print in case verbose
        mode is True.
        """
        self.logger.warn(msg)
        self.prints(msg, only_when_verbose=True)

    def exception(self, error):
        """ It uses the logger to log exception
        """
        self.logger.exception(error)

    def error(self, msg):
        """ If uses the logger to log as error and also print in case verbose
        mode is True.
        """
        self.logger.error(msg)
        self.prints(msg)  # always print errors regardless verbose mode

    def debug(self, msg):
        """ If uses the logger to log as debug only. It prints if the prints
        argument is True and verbose mode is True.
        """
        self.logger.debug(msg)
