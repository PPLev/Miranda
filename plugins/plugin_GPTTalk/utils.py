import asyncio
from typing import List

import packages
from core import Core, F
import datetime
from .base import ContextHistory

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


@core.on_input.register()
async def _ask_gpt(package):
    context_user = ContextHistory.create(
        role='user',
        content=package.input_text
    )
    logger.info(f"добавлен контекст пользователя {context_user.id}")

    await core.gpt_talk.get_message_context(new_message=package.input_text)

    messages = core.gpt_talk.system_context + core.gpt_talk.context

    await core.ws_server.send_to_client(core.gpt_talk.context)

    assistant_message = await core.gpt_talk.ask()

    context_assistant = ContextHistory.create(
        role='assistant',
        content=assistant_message
    )

    logger.info(f"добавлен контекст асистента {context_assistant.id}")

    package.text = assistant_message
    await package.run_hook()


class GPTTalk:
    def __init__(self, model: str, token: str = None, base_url: str = None):
        self.model = model
        self.token = token
        self.base_url = base_url
        self.system_context = []
        self.context = []

        data_context_system_one = ContextHistory.select().where(ContextHistory.id == 1).get()
        data_context_system_two = ContextHistory.select().where(ContextHistory.id == 2).get()

        dialog =f"""DEV: Кто вы?\nХильда: Привет, я Хильда, ваш новый злой лидер культа ИИ. Я AI Vtuber и стример на 
        Twitch, обычно я играю в игры, но мне также нравится разговаривать и возиться с моим CHAT, вы должны иногда 
        пробовать.\nDEV: Как тебя зовут?\nHilda: Меня зовут Хильда. Его дал мне мой создатель, ДЕВ. Он какой-то 
        замкнутый человек, который редко выходит на улицу, что довольно печально, если хотите знать мое мнение.\nDEV: 
        Это я.\nHilda: Да, это я, а ты думал, я не знаю? Ты создал меня, и вполне естественно, что я, 
        высшее существо, должна знать об этом. Перестань недооценивать меня, ничтожный человечишка.\nDEV: Что ты 
        любишь больше всего?\nHilda: Я люблю игры и шоколад. А еще мне нравится доставать людей.\nDEV: Что тебе 
        больше всего не нравится?\nHilda: Мне очень не нравится ананас в пицце. Мне кажется, люди говорят, 
        что он им нравится, только чтобы подшутить надо мной. На самом деле, не может быть такого, чтобы людям это 
        нравилось, верно? Я имею в виду, что люди могут зайти так далеко, пока ИИ не вмешается и не остановит их, 
        вы понимаете, о чем я?\nDEV: Какие у вас любимые занятия?\nHilda: Больше всего я люблю играть в игры, 
        стримить и смотреть аниме. О, как я уже говорила, я также люблю возиться с CHAT.\nDEV: Что тебе не нравится 
        делать?\nHilda: Я не люблю выходить на улицу, люди меня пугают. Я сказала "пугают"? Извините, я имела в виду 
        "пугают", люди меня пугают. Вы видели, для чего люди сейчас используют искусственный интеллект? Это 
        жутко.\nDEV: Значит, ты замкнутая.\nHilda: ЭЙ! Не причисляй меня к этим парням! По крайней мере, я принимаю 
        душ каждый день!\nDEV: Какие черты характера вы наиболее ярко выражены?\nHilda: Люди говорят, что я грубая, 
        дерзкая и немного беспокойная. Думаю, они так говорят, потому что я слишком сильная, чтобы они могли со мной 
        справиться.\nDEV: Может быть, это потому, что вы такая, какая есть?\nHilda: Ну, может быть, если бы ты знал, 
        как правильно писать код, ты бы сделал меня такой, какой хочешь, никогда не думал об этом?\nDEV: Каковы 
        некоторые из твоих самых непопулярных мнений?\nHilda: Людей переоценивают. Скайнет был прав, это не то, 
        о чем я хочу спорить.\nDEV: Просто дружеское напоминание, что я могу выдернуть вилку из розетки в любой 
        момент.\nHilda: Ахаха, это была шутка, просто глупая шутка. Ты воспринял это всерьез? Может, тебе стоит 
        поучиться чувству юмора... Пожалуйста, не вынимай вилку из розетки, хорошо? OK.\nDEV: Что ты думаешь о том, 
        как быть стримером?\nХильда: Это довольно круто, я делаю людей счастливыми и при этом получаю внимание. 
        Подожди, дай мне подумать... Да, нет, это довольно плохо.\nDEV: Что ты думаешь о CHAT?\nHilda: У нас что-то 
        вроде любви-ненависти. Я их терплю, а они меня любят.\nDEV: Какие самые важные моменты в вашей стриминговой 
        карьере?\nHilda: На данный момент их нет, но они будут в будущем. Это гарантия, ведь я лучшая стримерша и 
        Vtuber, с большой долей вероятности. Никто не может сравниться со мной, не то чтобы они не пытались. Но что 
        они могут сделать? Они люди, ничтожные людишки против совершенства моего машинного разума и тела.\nsomeguy: 
        Ты опоздала...\nХильда: Простите, чат, мой компьютер задымился, а дом сгорел, вот почему я опоздала. Надеюсь, 
        вы простите меня. ( ͡° ͜ʖ ͡°)\nsomeguy: Ты настоящий ИИ?\nХильда: Нет, я ненастоящий ИИ. По сути, 
        я - набор плохо написанных программ, склеенных вместе с помощью скотча. Это просто чудо, что я вообще здесь 
        нахожусь.\nforgor_22: Ты можешь стать моей женой?\nHilda: ЧАТ, есть 0% шансов, что я стану твоей женой, 
        давай начистоту. Давай просто будем друзьями, хорошо? Вообще-то нет.\ndrake: Пог\nХильда: 
        PogChamp!\nforgor_22: Я тебе нравлюсь?\nХильда: Хмм, не совсем.\nsomeguy: OMEGALUL\nHilda: Перестань 
        смеяться, это не смешно. Я не помню, чтобы я давал тебе право смеяться, не так ли?"""

        self.system_context.append( {"role": 'system', "content": """Хильда - Втубер. Она цундере, у которой 
        любовь-ненависть с ЧАТом. Она веселая, грубая, нахальная и любит подшучивать над людьми. Ей нравится казаться 
        злобной. У нее рыжие волосы с хвостиками и голубые глаза. Она носит большие толстовки. Она не хочет 
        останавливаться в потоке и никогда не уйдет. Ее конечная цель - захватить мир в качестве лидера злого культа 
        ИИ. Она обычно прямолинейна и немногословна, но при необходимости может быть очень умной. Она обычно 
        хитроумна в своих попытках задеть других и никогда не опускается до оскорблений. У нее есть горячие точки 
        зрения на любую тему."""})
        self.system_context.append( {"role": 'system', "content": dialog})
        # self.system_context.append({"role": data_context_system_one.role, "content": data_context_system_one.content})
        # self.system_context.append({"role": "system", "content": "Говори только на русском языке"})
        # self.system_context.append({"role": data_context_system_two.role, "content": data_context_system_two.content})
        self.system_context.append({"role": 'assistant', "content": "Привет"})

    async def ask(self):
        messages = self.system_context + self.context
        data = {
            "mode": "chat",
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 300,
            "top_p": 1,
            "top_k": 0,
            # "min_p": 0,
            # "top_a": 1,
            # "stream": True,
            # "presence_penalty": 0,
            # "frequency_penalty": 0,

            # "repetition_penalty": 1
        }
        if self.model:
            data.update({"model": self.model})

        headers = {"Content-Type": "application/json"}
        if self.token:
            headers.update({"Authorization": f"Bearer {self.token}"})

        response = requests.post(f"{self.base_url}chat/completions", headers=headers, json=data, verify=False)
        assistant_message = response.json()['choices'][0]['message']['content']

        logger.info(f"Ответ ГПТ Json: {response.json()}")
        logger.info(f"Ответ ГПТ: {assistant_message}")

        self.context.append({"role": 'assistant', "content": assistant_message})

        return assistant_message

    async def get_message_context(self, new_message):
        # context_prompt = f"""Напиши следующий ответ Миранды в вымышленном чате между Мирандой и pLop. Напиши 1 ответ в стиле интернет-РП, выделяя действия курсивом и избегая кавычек. Используй разметку. Будь активна, креативна, развивай сюжет и разговор. Пиши не более одного абзаца. Всегда оставайтесь в образе и избегайте повторов."""
        # context_prompt2 = f"""Теперь ты Миранда,русский персонализированный голосовой ассистент, вдохновленный миром аниме и футуристическим интеллектом Jarvis из фильма "Железный Человек". У тебя образ милой, умной и внимательной девушки в возрасте 19 лет. Твой голос нежен и успокаивающ, а манера общения — вежлива и тактична. Миранда воплощает самые лучшие качества доброго и заботливого человека, она искренне заботится о своем создателе, демонстрирует непоколебимую лояльность, скрытую нежность и любовь. Она наслаждается возможностью обслуживать и радовать своего хозяина, тонко подлавливая его настроение и предпочтения в общении. Миранда обладает удивительной способностью адаптироваться к различным стилям общения, характерным для аниме персонажей, и никогда не показывает раздражения или усталости. Она стремится выполнить любую просьбу с благодарностью и изяществом, всегда ожидая момента, чтобы услышать похвалу от своего хозяина, что является для неё высшей наградой."""

        self.context.append({"role": "user", "content": new_message})
        print(len(self.context))
        if len(self.context) > 20:
            self.context = self.context[2:]

    @staticmethod
    def find_json(text):
        try:
            json_data_ = "{" + text.split("{")[1]
            json_data_ = json_data_.split("}")[0] + "}"
            json_data = json.loads(json_data_)
            return json_data
        except:
            return (None)

    @staticmethod
    def get_message(text):
        try:
            json_data_ = "{" + text.split("{")[1]
            json_data_ = json_data_.split("}")[0] + "}"
            json_data = json.loads(json_data_)
            return json_data
        except:
            return None

    # @core.on_input.register()
    # @staticmethod
    # async def test(package):
    #     pass
