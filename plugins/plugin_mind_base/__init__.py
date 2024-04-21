from core import Core
from .gpt_util import *

core = Core()


async def start(core: Core):
    manifest = {
        "name": "Плагин знаний",
        "version": "1.0",

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    raise Exception("Пока не доделан - сорян)")
