from aiohttp import web

import inspect
import json
import logging
import os
import sys
import requests

logger = logging.getLogger("root")

from core import Core, F

core = Core()


class HTTPServer:
    def __init__(self, host, port):
        self.site = None
        self.runner = None
        self.host = host
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/', self.handle)

    async def handle(self, request):
        with open('index.html', 'r', encoding='utf-8') as f:
            return web.Response(text=f.read(), content_type='text/html', charset='utf-8')

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        logger.info(f"Страница запущена http://localhost:8999/")
        print('"http://localhost:8999/"')
