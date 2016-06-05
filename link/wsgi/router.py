# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter
from b3j0f.utils.path import lookup

from link.wsgi import CONF_BASE_PATH

from inspect import isclass
from re import match
import traceback
import logging


@Configurable(
    paths='{0}/router.conf'.format(CONF_BASE_PATH),
    conf=category(
        'ROUTER',
        Parameter(name='urlpatterns', ptype=dict),
        Parameter(name='middlewares', ptype=list)
    )
)
class Router(object):
    """
    Request dispatcher.

    Contains URL patterns as dict:

     - a regex to match the URL as key
     - a dict associated HTTP methods to Python callable objects

    Also contains list of middlewares (Python classes) to apply.

    Example of configuration:

    .. code-block:: javascript

       {
          "ROUTER": {
             "urlpatterns": {
                "^/hello$": {
                   "GET": "python.path.to.hello_function"
                }
             },
             "middlewares": [
                "python.path.to.MiddlewareClass"
             ]
          }
       }
    """

    @property
    def urlpatterns(self):
        if not hasattr(self, '_urlpatterns'):
            self.urlpatterns = None

        return self._urlpatterns

    @urlpatterns.setter
    def urlpatterns(self, value):
        if value is None:
            value = {}

        self._urlpatterns = value

    @property
    def middlewares(self):
        if not hasattr(self, '_middlewares'):
            self.middlewares = None

        return self._middlewares

    @middlewares.setter
    def middlewares(self, value):
        if value is None:
            value = []

        self._middlewares = value

    def __init__(self, urlpatterns=None, middlewares=None, *args, **kwargs):
        """
        :param urlpatterns: URL patterns config (used to override config file)
        :type urlpatterns: dict

        :param middlewares: Middlewares config (used to override config file)
        :type middlewares: list
        """

        super(Router, self).__init__(*args, **kwargs)

        self.logger = logging.getLogger('link.wsgi.router')

        if urlpatterns is not None:
            self.urlpatterns = urlpatterns

        if middlewares is not None:
            self.middlewares = middlewares

        self.objcache = {}

    def dispatch(self, req, resp):
        """
        Dispatch request to handler, which will fill response.

        :param req: request object
        :type req: link.wsgi.req.Request

        :param resp: response object
        :type resp: link.wsgi.resp.Response
        """

        for urlpattern in self.urlpatterns:
            # check URL for every configured patterns
            if match(urlpattern, req.path) is not None:
                self.logger.debug('URLPattern({0})'.format(urlpattern))
                route = self.urlpatterns[urlpattern]

                # check if request method is allowed for route
                if req.method in route:
                    try:
                        h = hash('{0}{1}'.format(urlpattern, req.method))

                        # check if handler has already been instantiated
                        if h not in self.objcache:
                            # fetch handler, instantiate it if it's a class
                            handler = lookup(route[req.method])

                            if isclass(handler):
                                # the handler for a class is a method
                                # the method's name is the request method
                                handler = getattr(
                                    handler(),
                                    req.method.lower()
                                )

                            self.objcache[h] = handler

                        else:
                            handler = self.objcache[h]

                        # instantiate middlewares if needed
                        middlewares = []

                        for middleware in self.middlewares:
                            h = hash(middleware)

                            if h not in self.objcache:
                                self.objcache[h] = lookup(middleware)()

                            middlewares.append(self.objcache[h])

                        # apply middlewares on request/response/handler
                        abort = False
                        for middleware in middlewares:
                            if middleware.before(req, resp, handler):
                                abort = True
                                break

                        # if a middleware returned True, the request is aborted
                        if abort:
                            self.logger.debug('Request aborted')
                            break

                        # pass request/response to the handler
                        handler(req, resp)

                        # apply middlewares on request/response/handler again
                        for middleware in reversed(middlewares):
                            if middleware.after(req, resp, handler):
                                break

                    except Exception:
                        # if any error happens, return a 500 internal error
                        resp.status = 500
                        resp.content = traceback.format_exc()

                else:
                    # if the method was not configured for the route, return a
                    # 405 method not allowed
                    resp.status = 405
                    resp.content = 'Unkown method: {0}'.format(req.method)

                # here a handler was found, successfully executed or not
                # we do not need to check for another urlpattern
                break

        else:
            # no urlpattern matched, return a 404 not found
            resp.status = 404
            resp.content = 'No route matching URL: {0}'.format(req.path)
