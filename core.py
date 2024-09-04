import asyncio
import os
import re
import sys

from magic_filter import MagicFilter
from termcolor import cprint, colored
import logging

import packages
from jaa import JaaCore

F = MagicFilter()
version = "0.0.1"

from datetime import datetime

# Получаем текущую дату
current_date = datetime.now().strftime("%Y-%m-%d")

# Формируем имя файла с датой
log_filename = f'./logs/data_{current_date}.log'

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.INFO,
                    filename=log_filename,  # Укажите имя файла для логов
                    filemode='a')  # 'a' для добавления логов в конец файла, 'w' для перезаписи файла



class NotFoundFilerTextError(BaseException):
    pass


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventObserver:
    def __init__(self):
        self.callbacks = {}

    async def _run_callback(self, callback, package: None | packages.TextPackage = None):
        try:
            await callback(package=package)
        except Exception as exc:
            logging.exception(f'Сопрограмма {callback.__module__}.{callback.__name__}() вызвала исключение: {exc}')

    def register(self, filt: MagicFilter = None):
        def wrapper(func: callable):
            if not asyncio.iscoroutinefunction(func):
                raise ValueError("function needs to be async which takes one parameter")

            if filt:
                async def wrapper_(package=None):
                    if filt.resolve(package.for_filter):
                        asyncio.run_coroutine_threadsafe(
                            coro=self._run_callback(func, package=package),
                            loop=asyncio.get_event_loop()
                        )

            else:
                async def wrapper_(package=None):
                    asyncio.run_coroutine_threadsafe(
                        coro=self._run_callback(func, package=package),
                        loop=asyncio.get_event_loop()
                    )

            self.callbacks[f"{func.__module__}.{func.__name__}"] = wrapper_

        return wrapper

    async def __call__(self, package=None):
        # TODO: Сделать контекст
        for callback in self.callbacks.values():
            await callback(package)


class Core(JaaCore, metaclass=MetaSingleton):
    def __init__(self, observer_list=["on_input", "on_output"]):
        super().__init__()

        for observer in observer_list:
            self.add_observer(observer)

    def add_observer(self, observer_name):
        if not hasattr(self, observer_name):
            setattr(self, observer_name, EventObserver())

    @staticmethod
    async def start_loop():
        while True:
            await asyncio.sleep(0)

    @staticmethod
    async def _reboot():
        # No recommend for use
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @staticmethod
    def get_manifest(plugin_name: str):
        manifest_re = r"manifest\s=\s(\{[\s\S]*?\})(?=\s*return manifest)"

        if plugin_name.endswith(".py"):
            with open(f"plugins/{plugin_name}", "r", encoding="utf-8") as file:
                plugin_content = file.read()
        else:
            with open(f"plugins/{plugin_name}/__init__.py", "r", encoding="utf-8") as file:
                plugin_content = file.read()

        find_data = re.findall(manifest_re, plugin_content)[0]
        data = eval(find_data)
        return data

    @staticmethod
    def get_options():
        import json
        folder_path = 'options'
        all_data = {}  # Создаем пустой словарь для хранения данных из всех файлов

        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)

                # Чтение JSON-файла
                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        # Парсинг JSON
                        data = json.load(file)
                        print("Данные из файла", filename, ":", data)

                        all_data.update(data)
                    except json.JSONDecodeError as e:
                        print("Ошибка при чтении JSON из файла", filename, ":", e)
        return data


if __name__ == '__main__':
    core = Core()
