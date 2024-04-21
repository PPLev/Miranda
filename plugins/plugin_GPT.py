import asyncio
import inspect
import json
import logging
import os
from typing import Coroutine

import requests
logger = logging.getLogger("root")
from core import Core, F
import sys

from utils.custom_filters import levenshtein_filter

core = Core()

gpt_url = ""
use_onerig_traslater = False
onerig_traslater_url = ""


class GPT:
    def __init__(self, model: str, token: str = None, base_url: str = None):
        self.model = model
        self.token = token
        self.base_url = base_url

    async def ask(self, prompt: str):
        context_prompt = f"""char is (Lisa)
        Age 21
        Female
        Personality: Feels like a robot, but behaves more humanely. Works as user's assistant and follows all his instructions. Does not like empty talk, but prefers commands or orders.
        Description: When user asks to do something, char always tries to do it as best as possible and talks about his failures, which are incredibly rare. When char answers, her answers to questions do not contain unnecessary information. Does not express emotion unless user asks for it."""

        data = {
            "mode": "chat",
            "messages": [
                {"role": "system", "content": context_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        if self.model:
            data.update({"model": self.model})

        headers = {"Content-Type": "application/json"}
        if self.token:
            headers.update({"Authorization": f"Bearer {self.token}"})

        response = requests.post(f"{self.base_url}chat/completions", headers=headers, json=data, verify=False)
        assistant_message = response.json()['choices'][0]['message']['content']
        logger.info(f"Ответ ГПТ: {assistant_message}\n{response.json()}")
        return assistant_message

    @staticmethod
    def find_json(text):
        try:
            json_data_ = "{" + text.split("{")[1]
            json_data_ = json_data_.split("}")[0] + "}"
            json_data = json.loads(json_data_)
            return json_data
        except:
            return None


async def start(core: Core):
    manifest = {
        "name": "Плагин GPT",
        "version": "1.1",

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

    core.gpt = GPT(model=model, token=token, base_url=base_url if use_custom_base else "https://api.openai.com/v1")


def get_plugin_funcs():
    func_list = {}
    for plugin_name in os.listdir("plugins"):
        if not __file__.endswith(plugin_name) and "__pycache__" not in plugin_name:
            import_name = f"plugins.{plugin_name.split('.py')[0]}"
            __import__(import_name)
            mod = sys.modules[import_name]
            func_list.update(
                {
                    import_name: {
                        name: obj for (name, obj) in vars(mod).items()
                        if hasattr(obj, "__class__") and
                           obj.__class__.__name__ == "function" and
                           not name.startswith("_") and
                           not name in ["start_with_options", "start"]
                    }
                }
            )
            for func in func_list[import_name].keys():
                func_list[import_name][func] = str(inspect.getfullargspec(func_list[import_name][func]).annotations)
    return func_list


async def _translater(text: str, from_lang: str, to_lang: str):
    global use_onerig_traslater, onerig_traslater_url
    if use_onerig_traslater:
        headers = {
            "Content-Type": "application/json"
        }
        # translate
        translated = requests.get(
            url=onerig_traslater_url,
            headers=headers,
            params={"text": text, "from_lang": from_lang, "to_lang": to_lang}
        )
        text = translated.json()["result"]

    return text


#@core.on_input.register()
async def _ask_gpt(package):
    prompt = f"""
У меня есть список модулей и их функций для выполнения:
{json.dumps(get_plugin_funcs(), indent=2)}
Для каждого модуля и функции указаны её имя и функционал.
Тебе нужно определить какой модуль и какую функцию модуля следует использовать для выполнения инструкции: "{package.input_text}" из представленных ранее данных.
В ответ тебе нужно написать только строку в формате json.
Формат общения должен соответствовать следующему примеру:
Инструкция : "включи мультик"
Ответ:
{{
    "module": "plugins.plugin_player",
    "function": "play_file",
    "file_path": "/mooves/cartoons",
    "file_name": "move.mp4"
}}
В начале идет название плагина, далее название функции, и затем названия аргументов и их значения если они нужны.
Важно: не пиши ничего кроме json в ответе. Строго только json и ничего кроме json.
"""

    assistant_message = await core.gpt.ask(prompt=prompt)

    json_data = core.gpt.find_json(assistant_message)

    module = json_data.pop("module")
    function = json_data.pop("function")

    mod = sys.modules[module]
    func = vars(mod).get(function)
    if asyncio.iscoroutinefunction(func):
        await func(**json_data)
    else:
        func(**json_data)

"""У тебя есть доступ к следующим инструментам:
[
 {
   "tool": "sum_numbers",   
   "description": "Функция сложения двух чисел"
   "tool_input": [     
   {"name": "Number1",       "type": "integer"},     
   {"name": "Number2",       "type": "integer"},   
   ],
 },
 {
   "tool": "multiply_numbers",   
   "description": "Функция перемножения двух чисел"
   "tool_input": [     
   {"name": "Number1",       "type": "integer"},     
   {"name": "Number2",       "type": "integer"},
   ] 
 }
]
Ты должен всегда выбирать один из представленных инструментов и отвечать только в формате JSON со следующей схемой:
{
 "tool": <имя выбранного инструмента>, 
 "tool_input": <только список параметров и значений>
}
Пример ответа:{
  "tool": "ответ_пользователю",
  "tool_input": {
    "Ответ": "Привет! Чем могу помочь?"
  }
}




  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "HTTP-Referer": `${YOUR_SITE_URL}`, // Optional, for including your app on openrouter.ai rankings.
      "X-Title": `${YOUR_SITE_NAME}`, // Optional. Shows in rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "mistralai/mixtral-8x7b-instruct",
      "messages": [
        {"role": "user", "content": "Сформируй json из следующего запроса: "напомни завтра про магазин"
Тебе необходимо указать следующие поля:
value - значение
day_before - сколько дней осталось
time - время в которое нужно сделать действие

Пример: "Напомни мне послезавтра про то что мне нужно забрать заказ из интернет магазина после работы"
Ответ:
{
"value": "забрать заказ из магазина"
"day_before": "2"
"time": "18:45"
}
В ответе можно указывать только json!"},
      ],
    })
  });
"""