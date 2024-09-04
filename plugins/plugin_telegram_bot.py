import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

from core import Core
import packages
from utils.clear_text import *

router = Router()

bot: Bot
dp: Dispatcher

nl = "\n"

core = Core()

logger = logging.getLogger("root")


@router.message(Command("start"))
async def start_command_handler(msg: types.Message, *args, **kwargs):
    print(f"пользователь с ID:  {msg.from_user.id} пытается залезть в бота")
    if msg.from_user.id not in kwargs["bot"].allow_ids:
        await msg.reply(
            text="Только хозяин может меня использовать!"
        )
        return

    await msg.reply("Рада вас видеть хозяин")


@router.message(Command("clear_context"))
async def clear_context_command_handler(msg: types.Message, *args, **kwargs):
    print(f"пользователь с ID:  {msg.from_user.id} пытается залезть в бота")
    await core.gpt_talk.clear_context()

    # if msg.from_user.id not in kwargs["bot"].allow_ids:

    await msg.reply("Контекст почищен")


@router.message(F.text)
async def msg_handler(msg: types.Message, *args, **kwargs):
    logger.info(f"Из ТГ от {msg.from_user.username} пришло сообщение из ТГ  : {msg.text}")

    if msg.from_user.id not in kwargs["bot"].allow_ids:
        await msg.reply(
            text="Только хозяин может меня использовать!"
        )
        return

    async def answer(packagew: packages.TextPackage):

        bot: Bot = kwargs["bot"]
        await bot.send_message(
            text=packagew.text,
            chat_id=msg.from_user.id
        )
        packageq = packages.TextPackage(input_text=packagew.text, core=core, hook=packages.NULL_HOOK)
        await core.on_output(packageq)

    package = packages.TextPackage(input_text=msg.text, core=core, hook=answer)
    await core.on_input(package)


@router.message(F.voice)
async def voice_handler(msg: types.Message, *args, **kwargs):
    if msg.from_user.id not in kwargs["bot"].allow_ids:
        await msg.reply(
            text="Только хозяин может меня использовать!"
        )
        return
    file_id = msg.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "last_bot_voice.wav")
    text = core.recognize_file("last_bot_voice.wav")

    async def answer2(packagew: packages.TextPackage):
        bot: Bot = kwargs["bot"]
        await bot.send_message(
            text=packagew.text,
            chat_id=msg.from_user.id
        )
        packageq = packages.TextPackage(input_text=packagew.text, core=core, hook=packages.NULL_HOOK)
        await core.on_output(packageq)

    package = packages.TextPackage(input_text=text, core=core, hook=answer2)
    await core.on_input(package)


async def run_client(bot_token, allow_isd):
    global bot, dp
    try:
        bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
        bot.allow_ids = allow_isd
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(router)

    except:
        return

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def stop_client():
    global dp
    try:
        await dp.stop_polling()
    except:
        pass


async def start(core: Core):
    manifest = {
        "name": "Плагин телеграм бота",
        "version": "1.0",

        "default_options": {
            "bot_token": "12345:qwerty",
            "allow_isd": [12345, 12345]
        },
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    bot_token = manifest["options"]["bot_token"]
    allow_isd = manifest["options"]["allow_isd"]
    asyncio.run_coroutine_threadsafe(run_client(bot_token, allow_isd), asyncio.get_running_loop())
