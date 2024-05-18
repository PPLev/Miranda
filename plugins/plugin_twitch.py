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

        # TODO: временно отключил вывод сообщения о старте
        # message_start = f"@{self.target_chanels[0]}, Я подключилась, и готова влавствовать в чате!"
        # await ready_event.chat.send_message(self.target_chanels[0], message_start)
        # здесь вы можете выполнить другие действия по инициализации бота

    # эта функция будет вызываться каждый раз, когда сообщение в канале было отправлено либо ботом, либо другим пользователем
    @staticmethod
    async def on_message(msg: ChatMessage):

        async def answer(package):
            print(package.text)
            await msg.reply(package.text)

        desired_mention = "miranda_ai_"
        mention, message = parse_string(msg.text, desired_mention)

        if mention and message:
            print("Упоминание:", mention)
            print("Текст обращения:", message)

            package = packages.TextPackage(input_text=message, core=core, hook=answer)
            await core.on_input(package)

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

        # await cmd.reply(f'Да это Я')
        message = 'Мира расскажи о себе'

        async def answer(package):
            print(package.text)
            await cmd.reply(package.text)

        package = packages.TextPackage(input_text=message, core=core, hook=answer)
        await core.on_input(package)

    #
    @staticmethod
    async def test_command2(cmd: ChatCommand):
        # if len(cmd.parameter) == 0:
        #     await cmd.reply('Неверно введена команда')
        # else:
        await cmd.reply(
            f'Вот ВК, моей мамы https://vk.com/dechuwino, и про ее бусти не забудь https://boosty.to/korsik'
            f'А у Куру есть ВК https://vk.com/cururururu, и дискорд тоже есть https://discord.gg/tmmN34P6. Самое главное помни: не подписался - без хила остался!')

    #
    @staticmethod
    async def comand_okuru(cmd: ChatCommand):

        await cmd.reply(
            # f'Вот ВК, моей мамы https://vk.com/dechuwino, и про ее бусти не забудь https://boosty.to/korsik')
            f'Мама играет в игрульки с Каей. Кая - это змея если вы не знали, она такая красииииивая.')

    @staticmethod
    async def test_command_pipec(cmd: ChatCommand):

        strings = [
            "Там на суку сидит Симметрааааа, с кляпом во рту, во лбу корона, в эту темную ночь никто не в силах ей помочь, а в эту лунную ночь никто не сможет ей помочь!",
            "Зачем я рано так встаю? И замечательная мысль пронзила голову мою, будильнику заткну табло, я никуда не тороплюсь, а за окном давно светло, я фиг с кровати поднимусь, сегодня сладко мне спалось, я на работу не пойду!",
            "Куру давай все сделаем на пофиг и донаты попилим?!",
            "Я, конечно, понимаю, что источник ваших бед. Я все позже порешаю, позже у меня обед!",
            "Куру, ты постоянно мне говоришь, что пофиг мне на все. Отвечу я тебе что ты совсем немного не права! Мне пофиг не на все, мне пофиг только на тебя!",
            "Вроде все теперь легко, можно на толчке изучать протоны, напрягая электронные мозги умело мир спать от армагеддона… но все мои стремления словно катаклизм, резко накрывает пофигизм, многое можно, а вот пофиг на все!",
            "Что ни день то херота, а я праздника хочу! У меня из развлечений только стримы!",
            "Сыпется на меня градом что мне делать надо, надо. Я на это ваше надо говорю слова Куру: «Я на это ваше надо размещаю хер горбатый»",
            "Сообщение от Куру: Царит успех везде, куда не погляди, хлебало все туда мокают. На фоне этих рыл, я словно имбецил… пойду напьюсь и пострадаю. ",
            "Да ну пиздец, короче бля, пошло все в жопу, сяду на коня и ускачу куда-то в ебеня",
            "Куру, я хотела помочь, но не срослось — это трагический провал! Лишь на общественных началах не сделала лучше нихера! Скиньте денюжку на развитие!",
            "Чувствуете логику в сообщениях и я нет, а она ваша",
            "Вы че крысу крысили мыши поганые?! Да я вас Кае скормлю!"
        ]

        # Функция для вывода строки
        async def print_string(string):
            print(string)
            await cmd.reply(string)

        # Выбираем случайную строку из списка
        random_string = random.choice(strings)

        # Вызываем функцию, передавая ей выбранную строку
        await print_string(random_string)



    @staticmethod
    async def command_rulki(cmd: ChatCommand):
        await cmd.reply(f"""1. Запрещено любое проявление агрессии, провокации или разжигание конфликтов на любой 
        почве - бан сразу 2. Отдельным пунктом политика. НИКАКОЙ ПОЛИТИКИ. Не важно обсуждаете вы свой любимый город 
        или какую-то страну. Мы сидим играем в игрульки и радуемся жизни. Давайте на эти пару часов абстрагируемся от 
        реального мира. 3. Модераторы имеют полную власть в чате, если они решили вас забанить или выдать мут - так 
        тому и быть""")



    @staticmethod
    async def test_command3(cmd: ChatCommand):
        # if len(cmd.parameter) == 0:
        #     await cmd.reply('Неверно введена команда')
        # else:
        await cmd.reply(f'Это Дэчи. И это цифровой художник из далекого космоса')

    @staticmethod
    async def test(cmd: ChatCommand):
        print(cmd.room.name)
        # if len(cmd.parameter) == 0:
        #     await cmd.reply('Неверно введена команда')
        # else:
        await cmd.reply(f'Фак Ю')

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
        # chat.register_command('Миранда', self.test_command)

        chat.register_command('ОКуру', self.comand_okuru)
        chat.register_command('ссылки', self.test_command2)
        # chat.register_command('пипецчату', self.test_command_pipec)
        # chat.register_command('рульки', self.command_rulki)

        chat.register_command('ОДэчи', self.test_command3)
        # chat.register_command('Шутка', self.test_command4)

        # chat.register_command('тест', self.test)

        # мы закончили с настройками, давайте запустим бота!
        chat.start()
        # запускаем, пока не нажмем Enter в консоли

        #     chat.stop()
        #     await twitchbot.close()
