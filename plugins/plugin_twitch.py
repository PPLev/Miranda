import asyncio
import json
import os
import sys

import re

import packages
from core import Core
import logging

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio

logger = logging.getLogger("root")

core = Core()


async def start(core: Core):
    manifest = {
        "name": "Плагин TWITCH",
        "version": "0.1",
        "default_options": {
            "is_active": False,
        },

    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    app_id = manifest["options"]["app_id"]
    app_secret = manifest["options"]["app_secret"]
    target_chanels = manifest["options"]["target_chanels"]
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    twitch = Twitchclass(app_id=app_id, app_secret=app_secret, target_chanels=target_chanels, user_scope=USER_SCOPE)
    asyncio.run_coroutine_threadsafe(twitch.run(), asyncio.get_running_loop())


def parse_string(input_string, desired_mention):
    pattern = rf'@({desired_mention})\s+(.*)'  # Регулярное выражение с учетом конкретного упоминания
    match = re.match(pattern, input_string)
    if match:
        mention = match.group(1)  # Получаем упоминание (после символа @)
        message = match.group(2)  # Получаем текст обращения (после упоминания)
        return mention, message
    else:
        return None, None


class Twitchclass:
    def __init__(self, app_id: str, app_secret: str, target_chanels: list[str], user_scope):
        self.app_id = app_id
        self.app_secret = app_secret
        self.target_chanels = target_chanels
        self.user_scope = user_scope

    # Эта функция будет вызвана при срабатывании события READY, которое произойдет при запуске бота
    # @staticmethod
    async def on_ready(self, ready_event: EventData):
        print('Бот готов к работе, подключается к каналам')
        # присоединитесь к нашему целевому каналу, если вы хотите присоединиться к нескольким, либо вызовите join для каждого отдельно
        # или даже лучше передать список каналов в качестве аргумента
        await ready_event.chat.join_room(self.target_chanels)

        message_start = f"@{self.target_chanels[0]}, Мама, я подключилась, и готова влавствовать в чате!"
        await ready_event.chat.send_message(self.target_chanels[0], message_start)
        # здесь вы можете выполнить другие действия по инициализации бота

    # эта функция будет вызываться каждый раз, когда сообщение в канале было отправлено либо ботом, либо другим пользователем
    @staticmethod
    async def on_message(msg: ChatMessage):

        async def answer(package):
            await msg.reply(package.text)

        desired_mention = "miranda_ai_"
        mention, message = parse_string(msg.text, desired_mention)
        if mention and message:
            print("Упоминание:", mention)
            print("Текст обращения:", message)

            package = packages.TextPackage(input_text=message, core=core, hook=answer)
            await core.on_input(package)
        else:
            print("Нет обращения")
        # logger.info(f"TWITCH: '{msg}'")
        # print(msg)
        # print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

        # await msg.chat.send_message(msg.room.name, package.text)

        # await bot.send_message(
        #     text=package.text,
        #     chat_id=msg.from_user.id
        # )
        # await msg.reply("Это конечно все здорово, но пока я туплю)")

        # package = packages.TelegramAnswerPackage(input_text=msg.text, core=core, answer=msg.reply)
        # await core.on_input(package)
        # await package.answer("Мама, я тут")
        # TODO: тут нада отправка в ядро

    # эта функция будет вызываться каждый раз, когда кто-то подписывается на канал
    @staticmethod
    async def on_sub(sub: ChatSub):
        print(f'New subscription in {sub.room.name}:\\n'
              f'  Type: {sub.sub_plan}\\n'
              f'  Message: {sub.sub_message}')

    # эта команда будет вызываться каждый раз, когда будет выдана команда !reply
    @staticmethod
    async def test_command(cmd: ChatCommand):
        # if len(cmd.parameter) == 0:
        #     await cmd.reply('Неверно введена команда')
        # else:
        await cmd.reply(f'Да это Я')

    #
    @staticmethod
    async def test_command2(cmd: ChatCommand):
        # if len(cmd.parameter) == 0:
        #     await cmd.reply('Неверно введена команда')
        # else:
        await cmd.reply(
            f'Вот ВК, моей мамы https://vk.com/dechuwino, и про ее бусти не забудь https://boosty.to/korsik')

    @staticmethod
    async def test_command3(cmd: ChatCommand):
        # if len(cmd.parameter) == 0:
        #     await cmd.reply('Неверно введена команда')
        # else:
        await cmd.reply(f'Это Дэчи. И это цифровой художник из далекого космоса')

    @staticmethod
    async def test_command4(cmd: ChatCommand):
        async def answer(package):
            await cmd.reply(package.text)

        message = "Придумай шутку в одно предложение"
        package = packages.TextPackage(input_text=message, core=core, hook=answer)
        await core.on_input(package)

    async def send_message(self, chat: Chat, message: str):
        print(self.target_chanels)
        target_chanel = self.target_chanels[0]
        try:
            await chat.send_message(target_chanel, message)
        except:
            print("Ошибка ")

    async def run(self):
        # установите экземпляр twitch api и добавьте аутентификацию пользователей с некоторыми диапазонами
        twitchbot = await Twitch(self.app_id, self.app_secret)
        auth = UserAuthenticator(twitchbot, self.user_scope)
        token, refresh_token = await auth.authenticate()

        await twitchbot.set_user_authentication(token, self.user_scope, refresh_token)

        # создать экземпляр чата
        chat = await Chat(twitchbot)

        # зарегистрируйте обработчики для нужных вам событий

        # слушать, когда бот закончит запуск и будет готов присоединиться к каналам
        chat.register_event(ChatEvent.READY, self.on_ready)

        # # прослушивание сообщений чата
        chat.register_event(ChatEvent.MESSAGE, self.on_message)

        # # прослушивание подписок на каналы
        # chat.register_event(ChatEvent.SUB, self.on_sub)
        # есть больше событий, вы можете просмотреть их все в этой документации

        # # попривествовать человека
        # chat.register_event(ChatEvent.JOIN, self.on_message)

        # # попривествовать рейдеров
        # chat.register_event(ChatEvent.RAID, self.on_message)

        # # вы можете напрямую регистрировать команды и их обработчики, в данном случае будет зарегистрирована команда !reply
        chat.register_command('Mira', self.test_command)
        chat.register_command('Ссылки', self.test_command2)
        chat.register_command('ОДэчи', self.test_command3)
        chat.register_command('Шутка', self.test_command4)

        # мы закончили с настройками, давайте запустим бота!
        chat.start()
        # запускаем, пока не нажмем Enter в консоли

        #     chat.stop()
        #     await twitchbot.close()
