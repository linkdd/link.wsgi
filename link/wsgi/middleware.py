# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, Category
from link.utils.logging import LoggingObject
from link.wsgi import CONF_BASE_PATH


@Configurable(
    paths='{0}/middleware.conf'.format(CONF_BASE_PATH),
    conf=Category('MIDDLEWARE')
)
class Middleware(LoggingObject):
    """
    Middleware class.

    Applied before and after requests are handled.
    """

    def before(self, req, resp, handler):
        """
        Called before request is handled.

        :param req: request that will be handled
        :type req: link.wsgi.req.Request

        :param resp: response that will be returned
        :type resp: link.wsgi.resp.Response

        :param handler: handler that will be used
        :type handler: callable

        :return: True to abort request handling
        :rtype: boolean
        """

        raise NotImplementedError()

    def after(self, req, resp, handler):
        """
        Called after request is handled.

        :param req: request that was handled
        :type req: link.wsgi.req.Request

        :param resp: response that was returned
        :type resp: link.wsgi.resp.Response

        :param handler: handler that was used
        :type handler: callable
        """

        raise NotImplementedError()
