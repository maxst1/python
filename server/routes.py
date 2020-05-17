from aiohttp import web
from .handlers import root
from .handlers import encrypt
from .handlers import decrypt
from .handlers import train
from .handlers import hack
import aiohttp_jinja2

from . import config

def set_routes(app):
    app.router.add_routes([
        web.get('/', root.handler),
        web.post('/encrypt', encrypt.handler),
        web.post('/decrypt', decrypt.handler),
        web.post('/train', train.handler),
        web.post('/hack', hack.handler),
        web.static('/templates', config.CONFIG['templates_path']),
    ])