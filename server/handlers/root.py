import aiohttp
from aiohttp_jinja2 import template

@template('index.html')
async def handler(request):
    return {'result': 'hi, ok'}