from aiohttp import web

from ._app import create_app
from . import config

import logging
import sys

def set_logging():
    logging.basicConfig(level = 'INFO', stream = sys.stdout)

def main():
    app = create_app()
    set_logging()
    web.run_app(app, port = config.CONFIG['port'])


if __name__ == '__main__':
    main()