from core import Core, F
import asyncio
from .utils import *
core = Core()



async def start(core: Core):
    manifest = {
        "name": "Плагин HTTPServer",
        "version": "1.0",

        "default_options": {
            "host": "localhost",
            "port": 8080,
        },
    }
    return manifest



async def start_with_options(core: Core, manifest: dict):
    host = manifest["options"]["host"]
    port = manifest["options"]["port"]
    http_server = HTTPServer(host, port)

    asyncio.run_coroutine_threadsafe(http_server.start(), asyncio.get_running_loop())
