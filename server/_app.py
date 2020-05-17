from aiohttp import web
import jinja2
import aiohttp_jinja2

from .routes import set_routes
from . import config

import logging
import sys

def set_logger():
    logging.basicConfig(level = 'INFO', stream = sys.stdout)

def create_app():
    app = web.Application()
    aiohttp_jinja2.setup(
        app, 
        loader = jinja2.FileSystemLoader(config.CONFIG['templates_path'])
    )
    set_routes(app)
    return app
