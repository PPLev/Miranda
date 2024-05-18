from core import Core, F
from .utils import *
core = Core()


async def start(core: Core):
    manifest = {
        "name": "Плагин GPTTalk",
        "version": "1.0",

        "default_options": {
            "openai_completable": {
                "base_url": "http://127.0.0.1:5000/v1/",
                "model": None,
                "token": None,
            },
            "use_custom_base": True,
            "use_onerig_traslater": False,
            "onerig_traslater_url": "http://127.0.0.1:4990/translate"
        },
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    base_url = manifest["options"]["openai_completable"]["base_url"]
    model = manifest["options"]["openai_completable"]["model"]
    token = manifest["options"]["openai_completable"]["token"]
    use_custom_base = manifest["options"]["use_custom_base"]

    core.gpt_talk = GPTTalk(model=model, token=token,
                            base_url=base_url if use_custom_base else "https://api.openai.com/v1")
