import asyncio
import json
import os
import sys
import random

import re

import packages
from core import Core
import logging

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.chat.middleware import UserRestriction, StreamerOnly, ChannelRestriction
import asyncio

from utils.clear_text import *

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


class Twitchclass:
    def __init__(self, app_id: str, app_secret: str, target_chanels: list[str], user_scope):
        self.app_id = app_id
        self.app_secret = app_secret
        self.target_chanels = target_chanels
        self.user_scope = user_scope

    async def run(self):
        # установите экземпляр twitch api и добавьте аутентификацию пользователей с некоторыми диапазонами
        twitchbot = await Twitch(self.app_id, self.app_secret)

        helper = UserAuthenticationStorageHelper(twitchbot, self.user_scope)
        await helper.bind()

        # auth = UserAuthenticator(twitchbot, self.user_scope)
        # token, refresh_token = await auth.authenticate()

        # await twitchbot.set_user_authentication(token, self.user_scope, refresh_token)

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

        def register_commands(chat, commands, channel=None):
            for command, handler in commands.items():
                if channel:
                    chat.register_command(command, handler,
                                          command_middleware=[ChannelRestriction(allowed_channel=[channel])])
                else:
                    chat.register_command(command, handler)
            return chat

        # chat.register_command('тест', self.test, command_middleware=[ChannelRestriction(allowed_channel=['plop6912'])])
        plop6912_commands = {
            'тест': self.test,
        }
        register_commands(chat, plop6912_commands, 'plop6912')

        # Регистрация команд для канала 'curururu'
        curururu_commands = {
            'ОКуру': self.comand_curururu_okuru,
            'всибирь': self.comand_curururu_urls,
            'пипецчату': self.command_curururu_pipec,
            'рульки': self.command_curururu_rulki,
        }

        register_commands(chat, curururu_commands, 'curururu')

        # Регистрация команд для канала 'dechuwin0'
        dechuwin0_commands = {
            'ОДэчи': self.command_dechuwin0_odechu,
            'Шутка': self.command_dechuwin0_joke,
            'Ссылки': self.comand_dechuwin0_urls,
        }

        register_commands(chat, dechuwin0_commands, 'dechuwin0')

        # Команда, не требующая ограничения по каналу
        miranda_commands = {
            'Миранда': self.command_miranda
        }

        register_commands(chat, miranda_commands)

        # chat.register_command('ОКуру', self.comand_curururu_okuru,
        #                       command_middleware=[ChannelRestriction(allowed_channel=['curururu'])])

        # мы закончили с настройками, давайте запустим бота!
        chat.start()

        #     chat.stop()
        #     await twitchbot.close()

    # Эта функция будет вызвана при срабатывании события READY, которое произойдет при запуске бота
    async def on_ready(self, ready_event: EventData):
        logging.info('Бот готов к работе, подключается к каналам')
        # присоединитесь к нашему целевому каналу, если вы хотите присоединиться к нескольким, либо вызовите join для каждого отдельно
        # или даже лучше передать список каналов в качестве аргумента
        await ready_event.chat.join_room(self.target_chanels)

        # TODO: временно отключил вывод сообщения о старте
        # message_start = f"@{self.target_chanels[0]}, Я подключилась, и готова влавствовать в чате!"
        # await ready_event.chat.send_message(self.target_chanels[0], message_start)
        # здесь вы можете выполнить другие действия по инициализации бота

    # эта функция будет вызываться каждый раз, когда сообщение в канале было отправлено либо ботом, либо другим пользователем
    async def on_message(self, msg: ChatMessage):

        async def answer(package):
            logger.info(f'in {package.text}')

            await core.on_output(package)

            cleaned_text = clean_text(package.text)
            max_length = 400  # Установите предел символов для каждого блока
            chunks = preprocess_text(cleaned_text, max_length)

            for i, chunk in enumerate(chunks):
                logger.info(f'chunk {chunk}')
                try:
                    # await msg.reply(chunk)
                    await msg.chat.send_message(msg.room.name, chunk)
                except:
                    logger.error("Ошибка print_string")

        desired_mention = "miranda_ai_"
        mention, message = parse_string(msg.text, desired_mention)

        if mention and message:
            logger.info(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

            if msg.user.name in self.target_chanels:
                logger.info(f"Упоминание: {mention}")
                logger.info(f"Текст обращения: {message}")
                package = packages.TextPackage(input_text=message, core=core, hook=answer)
                await core.on_input(package)
            else:
                await msg.reply('Простите я отвечаю только владельцу канала')

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
        logger.info(f'New subscription in {sub.room.name}:\\n'
                    f'  Type: {sub.sub_plan}\\n'
                    f'  Message: {sub.sub_message}')

    # эта команда будет вызываться каждый раз, когда будет выдана команда !reply
    @staticmethod
    async def command_miranda(cmd: ChatCommand):
        message = 'Миранда расскажи о себе'

        async def answer(package):
            logger.info(package.text)
            await cmd.reply(package.text)

        package = packages.TextPackage(input_text=message, core=core, hook=answer)
        await core.on_input(package)

    @staticmethod
    async def comand_curururu_urls(cmd: ChatCommand):
        await cmd.reply(
            f'А у Куру есть ВК https://vk.com/cururururu , и дискорд тоже есть https://discord.gg/CVDmFS6Buk . Самое главное помни: не подписался - без хила остался!')

    @staticmethod
    async def comand_curururu_okuru(cmd: ChatCommand):
        await cmd.reply(
            f'Куру играет в игрульки с Каей. Кая - это змея если вы не знали, она такая красииииивая.')

    @staticmethod
    async def command_curururu_pipec(cmd: ChatCommand):
        strings = [
            "Чем дольше идет стрим тем Куру сильнее перестает дружить с голосовой",
            "Чувствуете логику в сообщениях? и я нет, а она ваша",
            "Вы че крысу скрысили мыши поганые?! Да я вас Кае скормлю!",
            "Кто к нам на стрим с мечом придет, тому мы в задницу этот меч и засунем",
            "Я, конечно, не очень рада вас всех видеть, но раз зашли на огонек то оставайтесь ",
            "Если у вас есть какие-то комментарии к стриму мы обязательно это все прочтем и порже…кхм… примем к сведению",
            "Ну, здравствуйте, кажется, я сейчас начну вам делать больно",
            "Врядли Куру сравнится с самыми похуистичными стримерами…он еще хуже",
            "Все кто забанены это заслужили! Поцы должны страдать хехехехе",
            "Куру…ты это…выпей капелек…что-ли",
            "Куру покажи им, где Кая зимует!",
            "Не говорите мне что тут опять стрим…гадство…опять работать",
            "Куру давай создадим клан воробушек-архимагов? Или клан боевых смертоносных корги…бррр…",
            "Хочешь сей, а хочешь куй, все равно получишь…",
            "Два тупорылых дегенерата. Дебил пупа и его друг-имбецил Лупа.",
            "Куру Встать! Смирно! Хвост в зубы! Упор лежа принять! Тридцать отжиманий! Хвост из пасти не выпасть! Не выпускать я сказала! Раз, два, три…",
            "Не забывайте, если вы хотите в пати к Куру, то хил платный, рес тоже"
        ]

        # Функция для вывода строки
        async def print_string(cmd: ChatCommand, message):
            logger.info(cmd.room.name)

            logger.info(message)
            # await cmd.reply(message)
            target_chanel = cmd.room.name

            try:
                await cmd.chat.send_message(target_chanel, message)
            except:
                logger.error("Ошибка print_string")

        # Выбираем случайную строку из списка
        random_string = random.choice(strings)

        # Вызываем функцию, передавая ей выбранную строку
        await print_string(cmd, random_string)

    @staticmethod
    async def command_curururu_rulki(cmd: ChatCommand):
        message = (f"""1. Запрещено любое проявление агрессии, провокации или разжигание конфликтов на любой 
        почве - бан сразу 2. Отдельным пунктом политика. НИКАКОЙ ПОЛИТИКИ. Не важно обсуждаете вы свой любимый город 
        или какую-то страну. Мы сидим играем в игрульки и радуемся жизни. Давайте на эти пару часов абстрагируемся от 
        реального мира. 3. Модераторы имеют полную власть в чате, если они решили вас забанить или выдать мут - так 
        тому и быть""")

        logger.info(cmd.room.name)
        target_chanel = cmd.room.name

        try:
            await cmd.chat.send_message(target_chanel, message)
        except:
            logging.error("Ошибка command_curururu_rulki")

    @staticmethod
    async def comand_dechuwin0_urls(cmd: ChatCommand):
        await cmd.reply(
            f'Вот ВК, моей мамы https://vk.com/dechuwino, и про ее бусти не забудь https://boosty.to/korsik'
        )

    @staticmethod
    async def command_dechuwin0_odechu(cmd: ChatCommand):
        await cmd.reply(f'Это Дэчи. И это цифровой художник из далекого космоса')

    @staticmethod
    async def test(cmd: ChatCommand):
        logger.info(cmd.room.name)
        target_chanel = cmd.room.name
        message = 'Тест пройден'

        try:
            await cmd.chat.send_message(target_chanel, message)
        except:
            logging.error("Ошибка test")

    @staticmethod
    async def command_dechuwin0_joke(cmd: ChatCommand):
        async def answer(package):
            await cmd.reply(package.text)

        message = "Придумай шутку в одно предложение"
        package = packages.TextPackage(input_text=message, core=core, hook=answer)
        await core.on_input(package)

    async def send_message(self, chat: Chat, message: str):
        logger.info(self.target_chanels)
        target_chanel = self.target_chanels[0]
        try:
            await chat.send_message(target_chanel, message)
        except:
            logging.error("Ошибка send_message")

def parse_string(input_string, desired_mention):
    pattern = rf'@({desired_mention})\s+(.*)'  # Регулярное выражение с учетом конкретного упоминания
    match = re.match(pattern, input_string)
    if match:
        mention = match.group(1)  # Получаем упоминание (после символа @)
        message = match.group(2)  # Получаем текст обращения (после упоминания)
        return mention, message
    else:
        return None, None