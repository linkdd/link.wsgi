Tutorial
========

In this tutorial, we will build a new package containing routes for our WSGI
applications and then deploy everything in a virtualenv.

Simple route
------------

A simple route is just a function which takes two parameters:

 - the received request
 - the response to fill

For example:

.. code-block:: python

   def hello(req, resp):
       resp.status = 200
       resp.content = 'Hello world'

See the API of :ref:`Request <modulereq>` and :ref:`Response <moduleresp>`
objects for more informations.

.. |Request| `

Class-based view
----------------

A route is just a callable object, if a class is used, then it will be
instantiated. The called handler is a method named after HTTP verbs:

.. code-block:: python

   class Hello(object):
       def get(self, req, resp):
           resp.status = 200
           resp.content = 'Hello world'

A simple middleware
-------------------

Middlewares are objects which are applied to the request before and after the
handling of the request.

It can be any objects respecting the API of the :ref:`Middleware <modulemid>`
class.

Example:

.. code-block:: python

   from link.wsgi.middleware import Middleware


   class MyMiddleware(Middleware):
      def before(self, req, resp, handler):
         # do something with request
         # do something with resp
         # do something with handler
         return False  # True to abort the request

      def after(self, req, resp, handler):
         # do something with request
         # do something with resp
         # do something with handler

Routes configuration
--------------------

Configuration file for the router is stored in:

.. code-block:: text

   $B3J0F_CONF_DIR/link/wsgi/router.conf

Here is an example of configuration where the simple route ``hello()`` is in
the package ``myapp.routes`` and the middleware ``MyMiddleware`` is in the
package ``myapp.middlewares``:

.. code-block:: javascript

   {
      "ROUTER": {
         "urlpatterns": {
            "^/hello$": {
               "GET": "mapp.routes.hello"
            }
         },
         "middlewares": {
            "myapp.middlewares.MyMiddleware"
         }
      }
   }

Deploying
---------

Prerequisites
~~~~~~~~~~~~~

Make sure the command ``virtualenv`` is available.

Creating virtualenv
~~~~~~~~~~~~~~~~~~~

Assuming you're in your Python package folder:

.. code-block:: bash

   $ virtualenv myapp-venv
   $ . ./myapp-venv/bin/activate
   (myapp-venv)$ pip install supervisord gunicorn link.wsgi
   (myapp-venv)$ python setup.py install

Configuring the whole thing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need the following *supervisord* service:

.. code-block:: ini

   [program:myapp]

   environment=B3J0F_CONF_DIR="%(ENV_VIRTUAL_ENV)s/etc"
   command=gunicorn link.wsgi.app:application
   stderr_logfile=%(ENV_VIRTUAL_ENV)s/myapp.log

Then we can add the following configuration files.

etc/link/wsgi/base.conf
***********************

.. code-block:: ini

   [LOGGING]

   log_level=info
   # log_name=myapp
   # log_file=/var/log/myapp.log

etc/link/wsgi/router.conf
*************************

See `Routes configuration`_.

Running everything
------------------

.. code-block:: bash

   (myapp-venv)$ supervisord
   (myapp-venv)$ supervisorctl start myapp
   (myapp-venv)$ curl http://localhost:8000/hello
   Hello world

