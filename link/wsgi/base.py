# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, Category, Parameter
from link.wsgi import CONF_BASE_PATH

import logging
import os


@Configurable(
    paths='{0}/base.conf'.format(CONF_BASE_PATH),
    conf=Category(
        'LOGGING',
        Parameter('log_name'),
        Parameter('log_level', value='info'),
        Parameter('log_path')
    )
)
class LoggingObject(object):
    """
    Class instantiating a logger.
    """

    @property
    def log_name(self):
        if not hasattr(self, '_log_name'):
            self.log_name = None

        return self._log_name

    @log_name.setter
    def log_name(self, value):
        if value is None:
            value = 'link.wsgi'

        self._log_name = value

    @property
    def log_level(self):
        if not hasattr(self, '_log_level'):
            self.log_level = None

        return self._log_level

    @log_level.setter
    def log_level(self, value):
        if value is None:
            value = 'info'

        self._log_level = value

    @property
    def log_path(self):
        if not hasattr(self, '_log_path'):
            self.log_path = None

        return self._log_path

    @log_path.setter
    def log_path(self, value):
        self._log_path = value

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            logname = '{0}.{1}'.format(self.log_name, self.__class__.__name__)
            self._logger = logging.getLogger(logname)
            level = getattr(logging, self.log_level.upper())
            self._logger.setLevel(level)

            if self.log_path is None:
                handler = logging.StreamHandler()

            else:
                logpath = os.path.abspath(
                    os.path.expanduser(self.log_path)
                )
                logdir = os.path.dirname(logpath)

                if not os.path.exists(logdir):
                    os.makedirs(logdir)

                handler = logging.FileHandler(logpath)

            self._logger.addHandler(handler)

        return self._logger
