import aiohttp
from aiohttp_jinja2 import template

@template('index.html')
async def handler(request):
    data = await request.post()
    return {'result': data['key']}