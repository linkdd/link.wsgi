# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category
from link.wsgi import CONF_BASE_PATH
from link.wsgi.router import Router
from link.wsgi.req import Request
from link.wsgi.resp import Response

import logging


@Configurable(
    paths='{0}/app.conf'.format(CONF_BASE_PATH),
    conf=category('APPLICATION')
)
class Application(object):
    """
    WSGI Application class.
    """

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

        self.router = Router()
        self.logger = logging.getLogger('link.wsgi.app')

    def __call__(self, environ, start_response):
        """
        WSGI application handler.

        :param environ: WSGI environ dict
        :type environ: dict

        :param start_response: WSGI response handler
        :type start_response: callable

        :return: response body
        :rtype: list
        """

        req = Request(environ)
        resp = Response(start_response)

        self.logger.debug(repr(req))
        self.router.dispatch(req, resp)
        self.logger.debug(repr(resp))

        return resp()


application = Application()
