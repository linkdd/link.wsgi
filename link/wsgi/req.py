# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, Category, Parameter

from link.wsgi import CONF_BASE_PATH
from link.wsgi.base import LoggingObject
from link.wsgi.url import parse_qs

from six.moves.urllib.parse import unquote
from six import string_types
from posixpath import normpath


@Configurable(
    paths='{0}/request.conf'.format(CONF_BASE_PATH),
    conf=Category(
        'REQUEST',
        Parameter('charsets')
    )
)
class Request(LoggingObject):
    """
    Request object encapsulating WSGI environ dict.
    """

    @property
    def charsets(self):
        if not hasattr(self, '_charsets'):
            self.charsets = None

        return self._charsets

    @charsets.setter
    def charsets(self, value):
        if value is None:
            value = ['utf-8', 'iso8859-1']

        if isinstance(value, string_types):
            value = [v.strip() for v in value.split(',')]

        self._charsets = value

    def __init__(self, environ, *args, **kwargs):
        """
        :param environ: WSGI environ dict
        :type environ: dict
        """

        super(Request, self).__init__(*args, **kwargs)

        self.environ = environ

    def __repr__(self):
        return 'Request(method={0}, path={1})'.format(self.method, self.path)

    @property
    def method(self):
        return self.environ['REQUEST_METHOD'].upper()

    @property
    def path(self):
        if not hasattr(self, '_path'):
            self._path = normpath(unquote(self.environ['PATH_INFO']))

        return self._path

    @property
    def query(self):
        if not hasattr(self, '_query'):
            self._query = parse_qs(self.environ['QUERY_STRING'])

        return self._query

    @property
    def content_type(self):
        return self.environ['CONTENT_TYPE']

    @property
    def content_length(self):
        return int(self.environ['CONTENT_LENGTH'] or 0)

    @property
    def content(self):
        if not hasattr(self, '_content'):
            self._content = None

            charsets = []

            content = self.environ['wsgi.input'].read(self.content_length)

            if self.content_type and 'charset=' in self.content_type:
                charsets.append(self.content_type.split('charset=')[1].strip())

            for charset in filter(lambda c: c not in charsets, self.charsets):
                charsets.append(charset)

            for c in charsets:
                try:
                    self._content = content.decode(c)

                except UnicodeDecodeError:
                    pass

                else:
                    break

            else:
                raise UnicodeDecodeError

        return self._content
