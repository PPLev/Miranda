import asyncio
import json
import threading

import packages
from core import Core

import logging
import logging.config

from plugin_NDI import utils
# TODO: проверить логи для главного файла
with open("logging.conf") as file:
    config = json.load(file)

logging.config.dictConfig(config)
logger = logging.getLogger("root")


async def core_start():
    core = Core()
    await core.init_plugins()
    await core.start_loop()


def run_asyncio():
    asyncio.run(core_start())


def main():
    # Запуск синхронной функции в отдельном потоке
    sync_thread = threading.Thread(target=utils.start_ndi)
    sync_thread.start()

    # Создание и запуск потока для асинхронной функции
    run_asyncio()


if __name__ == '__main__':
    main()
