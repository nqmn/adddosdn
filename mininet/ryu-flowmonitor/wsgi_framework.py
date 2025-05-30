#!/usr/bin/env python3
"""
WSGI Framework for SDN Controller Web Interface
Based on Ryu WSGI implementation with fallback mechanisms
"""

import inspect
import json
from types import MethodType
from collections import defaultdict

# Try to import Ryu WSGI components
try:
    from routes import Mapper
    from routes.util import URLGenerator
    import six
    from tinyrpc.server import RPCServer
    from tinyrpc.dispatch import RPCDispatcher
    from tinyrpc.dispatch import public as rpc_public
    from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
    from tinyrpc.transports import ServerTransport, ClientTransport
    from tinyrpc.client import RPCClient
    import webob.dec
    import webob.exc
    from webob.request import Request as webob_Request
    from webob.response import Response as webob_Response
    from ryu import cfg
    from ryu.lib import hub
    RYU_WSGI_AVAILABLE = True
    print("Full Ryu WSGI framework available")
except ImportError as e:
    print(f"Ryu WSGI framework not available: {e}")
    RYU_WSGI_AVAILABLE = False

# Try basic webob
try:
    import webob
    from webob.request import Request as webob_Request
    from webob.response import Response as webob_Response
    WEBOB_AVAILABLE = True
    print("Basic webob available")
except ImportError:
    print("webob not available - using fallback")
    WEBOB_AVAILABLE = False

# Configuration
DEFAULT_WSGI_HOST = '0.0.0.0'
DEFAULT_WSGI_PORT = 8080

HEX_PATTERN = r'0x[0-9a-z]+'
DIGIT_PATTERN = r'[1-9][0-9]*'


def route(name, path, methods=None, requirements=None):
    """Route decorator for controller methods"""
    def _route(controller_method):
        controller_method.routing_info = {
            'name': name,
            'path': path,
            'methods': methods,
            'requirements': requirements,
        }
        return controller_method
    return _route


class Request(object):
    """
    Simplified Request wrapper
    """
    def __init__(self, environ=None, charset="UTF-8", *args, **kwargs):
        if WEBOB_AVAILABLE and environ:
            self._webob_request = webob_Request(environ, charset=charset, *args, **kwargs)
            self.environ = environ
            self.method = self._webob_request.method
            self.path = self._webob_request.path
            self.path_info = self._webob_request.path_info
            self.urlvars = {}
        else:
            # Fallback implementation
            self.environ = environ or {}
            self.method = "GET"
            self.path = "/"
            self.path_info = "/"
            self.urlvars = {}
        
        self.start_response = None

    def __getattr__(self, name):
        if WEBOB_AVAILABLE and hasattr(self, '_webob_request'):
            return getattr(self._webob_request, name)
        return None


class Response(object):
    """
    Simplified Response wrapper
    """
    def __init__(self, body=None, status=200, charset="UTF-8", content_type="text/html", headers=None, *args, **kwargs):
        if WEBOB_AVAILABLE:
            self._webob_response = webob_Response(
                body=body, status=status, charset=charset, 
                content_type=content_type, *args, **kwargs
            )
            if headers:
                self._webob_response.headers.update(headers)
        else:
            # Fallback implementation
            self.status = status
            self.body = body or ""
            self.content_type = content_type
            self.charset = charset
            self.headers = headers or {}

    def __call__(self, environ, start_response):
        if WEBOB_AVAILABLE and hasattr(self, '_webob_response'):
            return self._webob_response(environ, start_response)
        else:
            # Simple fallback
            status_line = f"{self.status} OK"
            response_headers = [
                ('Content-Type', self.content_type),
                ('Content-Length', str(len(self.body)))
            ]
            response_headers.extend(self.headers.items())
            start_response(status_line, response_headers)
            return [self.body.encode(self.charset)]


class ControllerBase(object):
    """Base class for WSGI controllers"""
    special_vars = ['action', 'controller']

    def __init__(self, req, link, data, **config):
        self.req = req
        self.link = link
        self.data = data
        self.parent = None
        for name, value in config.items():
            setattr(self, name, value)

    def __call__(self, req):
        action = self.req.urlvars.get('action', 'index')
        if hasattr(self, '__before__'):
            self.__before__()

        kwargs = self.req.urlvars.copy()
        for attr in self.special_vars:
            if attr in kwargs:
                del kwargs[attr]

        return getattr(self, action)(req, **kwargs)


class SimpleMapper(object):
    """Simplified URL mapper when routes is not available"""
    
    def __init__(self):
        self.routes = []
        self.environ = None
    
    def connect(self, name, path, controller=None, requirements=None, action=None, conditions=None):
        """Add a route"""
        route_info = {
            'name': name,
            'path': path,
            'controller': controller,
            'action': action,
            'requirements': requirements or {},
            'conditions': conditions or {}
        }
        self.routes.append(route_info)
    
    def match(self, path_info=None, environ=None):
        """Match a path to a route"""
        if environ:
            path_info = environ.get('PATH_INFO', '/')
        
        for route in self.routes:
            if route['path'] == path_info:
                return {
                    'controller': route['controller'],
                    'action': route['action']
                }
        return None


class WSGIApplication(object):
    """Simplified WSGI Application"""
    
    def __init__(self, **config):
        self.config = config
        if RYU_WSGI_AVAILABLE:
            try:
                self.mapper = Mapper()
            except:
                self.mapper = SimpleMapper()
        else:
            self.mapper = SimpleMapper()
        
        self.registory = {}
        super(WSGIApplication, self).__init__()

    def _match(self, req):
        """Match request to route"""
        try:
            if hasattr(self.mapper, 'match'):
                if RYU_WSGI_AVAILABLE:
                    try:
                        return self.mapper.match(environ=req.environ)
                    except TypeError:
                        self.mapper.environ = req.environ
                        return self.mapper.match(req.path_info)
                else:
                    return self.mapper.match(req.path_info)
        except Exception as e:
            print(f"Route matching error: {e}")
            return None

    def __call__(self, environ, start_response):
        """WSGI application entry point"""
        req = Request(environ)
        req.start_response = start_response
        
        match = self._match(req)
        
        if not match:
            if WEBOB_AVAILABLE:
                return webob.exc.HTTPNotFound()(environ, start_response)
            else:
                # Simple 404 response
                response = Response("Not Found", status=404)
                return response(environ, start_response)

        req.urlvars = match
        
        # Create URL generator if available
        if RYU_WSGI_AVAILABLE:
            try:
                link = URLGenerator(self.mapper, req.environ)
            except:
                link = None
        else:
            link = None

        data = None
        name = match['controller'].__name__
        if name in self.registory:
            data = self.registory[name]

        controller = match['controller'](req, link, data, **self.config)
        controller.parent = self
        return controller(req)

    def register(self, controller, data=None):
        """Register a controller with routes"""
        def _target_filter(attr):
            if not inspect.ismethod(attr) and not inspect.isfunction(attr):
                return False
            if not hasattr(attr, 'routing_info'):
                return False
            return True
        
        methods = inspect.getmembers(controller, _target_filter)
        for method_name, method in methods:
            routing_info = getattr(method, 'routing_info')
            name = routing_info['name']
            path = routing_info['path']
            conditions = {}
            if routing_info.get('methods'):
                conditions['method'] = routing_info['methods']
            requirements = routing_info.get('requirements') or {}
            
            self.mapper.connect(name,
                                path,
                                controller=controller,
                                requirements=requirements,
                                action=method_name,
                                conditions=conditions)
        
        if data:
            self.registory[controller.__name__] = data


class WSGIServer(object):
    """Simplified WSGI Server"""
    
    def __init__(self, application, host=DEFAULT_WSGI_HOST, port=DEFAULT_WSGI_PORT, **config):
        self.application = application
        self.host = host
        self.port = port
        self.config = config
        print(f"WSGIServer initialized on {host}:{port}")

    def serve_forever(self):
        """Start serving (placeholder)"""
        print(f"WSGIServer would serve on {self.host}:{self.port}")
        print("Note: Actual server implementation requires additional setup")

    def __call__(self):
        self.serve_forever()


def start_service(app_mgr):
    """Start WSGI service"""
    for instance in app_mgr.contexts.values():
        if instance.__class__ == WSGIApplication:
            return WSGIServer(instance)
    return None
