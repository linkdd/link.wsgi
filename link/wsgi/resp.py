# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category
from b3j0f.utils.iterable import isiterable

from link.wsgi import CONF_BASE_PATH

from httplib import responses as httpresponses
from six import string_types
import json


@Configurable(
    paths='{0}/response.conf'.format(CONF_BASE_PATH),
    conf=category('RESPONSE')
)
class Response(object):
    """
    Response object encapsulating WSGI response handler.
    """

    def __init__(self, start_response, *args, **kwargs):
        """
        :param start_response: WSGI response handler
        :type start_response: callable
        """

        super(Response, *args, **kwargs)

        self._start_response = start_response
        self._headers = {}

    def __repr__(self):
        return 'Response(status={0})'.format(self.status)

    def __call__(self):
        """
        Execute WSGI response handler.

        :return: Response body
        :rtype: list
        """

        self._start_response(self.status, self.headers)
        return self.content

    @property
    def content(self):
        if not hasattr(self, '_content'):
            self.content = None

        return self._content

    @content.setter
    def content(self, value):
        if value is None:
            value = ''

        elif not isinstance(value, string_types) and not isiterable(value):
            try:
                value = json.dumps(value)

            except ValueError:
                value = str(value)

            value = value.splitlines()

        self._content = value
        self['Content-Length'] = sum([len(c) for c in self._content])

    @property
    def status(self):
        if not hasattr(self, '_status'):
            self.status = None

        return '{0} {1}'.format(self._status, httpresponses[self._status])

    @status.setter
    def status(self, value):
        if value is None:
            value = 200

        self._status = value

    @property
    def headers(self):
        return list(self._headers.items())

    def __getitem__(self, item):
        """
        Get header's value.

        :param item: header's name
        :type item: str

        :return: header's value
        """

        return self._headers.get(item, None)

    def __setitem__(self, item, value):
        """
        Set header's value.

        :param item: header's name
        :type item: str

        :param value: header's value
        """

        self._headers[item] = value
