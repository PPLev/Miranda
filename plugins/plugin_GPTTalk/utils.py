import asyncio
from typing import List

import packages
from core import Core, F
import datetime
from .base import ContextHistory
from .base import SystemContext

from openai import OpenAI

import inspect
import json
import logging
import os
from typing import Coroutine

import requests

logger = logging.getLogger(__name__)

from core import Core, F
import sys

from utils.custom_filters import levenshtein_filter

core = Core()

gpt_url = ""
use_onerig_traslater = False
onerig_traslater_url = ""



@core.on_input.register()
async def _ask_gpt(package):
    context_user = ContextHistory.create(
        role='user',
        content=package.input_text
    )
    logger.info(f"добавлен контекст пользователя {context_user.id}")

    await core.gpt_talk.set_message_context(new_message=package.input_text)

    # messages = core.gpt_talk.system_context + core.gpt_talk.context
    messages = core.gpt_talk.context

    await core.ws_server.send_to_client({'action': 'context', 'data': messages})
    await core.ws_server.send_to_client({'action': 'context', 'data': core.gpt_talk.context})

    assistant_message = await core.gpt_talk.ask()

    logger.debug(f"assistant_message: {assistant_message}")
    context_assistant = ContextHistory.create(
        role='assistant',
        content=assistant_message
    )

    # messages = core.gpt_talk.system_context + core.gpt_talk.context + core.gpt_talk.system_dop
    messages = core.gpt_talk.context + core.gpt_talk.system_dop

    logger.info(f"добавлен контекст асистента {context_assistant.id}")
    await core.ws_server.send_to_client({'action': 'context', 'data': messages})

    package.text = assistant_message
    await package.run_hook()



    # async def out(package):
    #      await core.on_output(package)
    #
    # package = packages.TextPackage("Гоорю", core, out)


class GPTTalk:
    def __init__(self, model: str, token: str = None, base_url: str = None, data: {} = None):
        self.model = model
        self.token = token
        self.base_url = base_url
        self.system_context = []
        self.context = []
        self.system_dop = []
        self.data = data

        data_context_system_one = SystemContext.select().where(SystemContext.id == 20).get()
        self.system_context.append({"role": 'system', "content": data_context_system_one.context})
        logger.info(self.system_context)

        self.system_context.append({"role": 'assistant', "content": 'Доброе утро хозяин'})

    def _get_data(self, messages):
        """Prepare the request data."""

        if messages:
            self.data.update({"messages": messages})

        if self.model:
            self.data.update({"model": self.model})

        return self.data

    def _prepare_request_headers(self):
        """Prepare the request headers."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers.update({"Authorization": f"Bearer {self.token}"})
        return headers

    def _handle_response(self, response):
        """Handle the HTTP response."""
        try:
            response.raise_for_status()
            response_json = response.json()
            logger.info(f"Ответ GPT Json: {response_json}")
            return response_json
        except requests.exceptions.HTTPError as e:
            logger.error(f"Request failed with status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
        except ValueError:
            logger.error("Invalid JSON response")
        return None

    def _process_response(self, response_json):
        """Process the JSON response."""
        try:
            assistant_message = response_json['choices'][0]['message']['content']
            logger.info(f"Ответ GPT: {assistant_message}")
            self.context.append({"role": 'assistant', "content": assistant_message})
            return assistant_message
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting message content: {e}")
        return 'Ошибка сервера ГПТ'

    async def ask(self):
        messages = self.system_context + self.context + self.system_dop
        data = self._get_data(messages)
        headers = self._prepare_request_headers()

        try:
            response = requests.post(f"{self.base_url}chat/completions", headers=headers, json=data, verify=False)
            response.raise_for_status()  # Поднимаем исключение для ошибок HTTP
            response_json = self._handle_response(response)
            if response_json:
                return self._process_response(response_json)
        except Exception as e:
            logger.error(f"Произошла непредвиденная ошибка: {e}")
            return self._process_response(response_json)
        return "хрень с сервером"

    async def set_message_context(self, new_message):
        self.context.append({"role": "user", "content": new_message})
        logger.info(f"Длинна собраного контекста {len(self.context)}")
        if len(self.context) > 20:
            self.context = self.context[2:]

    async def clear_context(self):
        self.context = []

    # @staticmethod
    # def find_json(text):
    #     try:
    #         json_data_ = "{" + text.split("{")[1]
    #         json_data_ = json_data_.split("}")[0] + "}"
    #         json_data = json.loads(json_data_)
    #         return json_data
    #     except:
    #         return (None)
    #
    # @staticmethod
    # def get_message(text):
    #     try:
    #         json_data_ = "{" + text.split("{")[1]
    #         json_data_ = json_data_.split("}")[0] + "}"
    #         json_data = json.loads(json_data_)
    #         return json_data
    #     except:
    #         return None

    # @core.on_input.register()
    # @staticmethod
    # async def test(package):
    #     pass

#
# def get_plugin_funcs():
#     func_list = {}
#     for plugin_name in os.listdir("plugins"):
#         if not __file__.endswith(plugin_name) and "__pycache__" not in plugin_name:
#             import_name = f"plugins.{plugin_name.split('.py')[0]}"
#             __import__(import_name)
#             mod = sys.modules[import_name]
#             func_list.update(
#                 {
#                     import_name: {
#                         name: obj for (name, obj) in vars(mod).items()
#                         if hasattr(obj, "__class__") and
#                            obj.__class__.__name__ == "function" and
#                            not name.startswith("_") and
#                            not name in ["start_with_options", "start"]
#                     }
#                 }
#             )
#             for func in func_list[import_name].keys():
#                 func_list[import_name][func] = str(inspect.getfullargspec(func_list[import_name][func]).annotations)
#     return func_list
#
#
# async def _translater(text: str, from_lang: str, to_lang: str):
#     global use_onerig_traslater, onerig_traslater_url
#     if use_onerig_traslater:
#         headers = {
#             "Content-Type": "application/json"
#         }
#         # translate
#         translated = requests.get(
#             url=onerig_traslater_url,
#             headers=headers,
#             params={"text": text, "from_lang": from_lang, "to_lang": to_lang}
#         )
#         text = translated.json()["result"]
#
#     return text
