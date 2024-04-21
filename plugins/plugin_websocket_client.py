import asyncio
import json
import os
import sys
import websockets

from core import Core
import logging

logger = logging.getLogger("root")

core = Core()


class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        while True:
            try:
                self.websocket = await websockets.connect(self.uri)
                print("Connected to server")
                break  # Выходим из цикла, если удалось подключиться
            except Exception as e:
                print(f"Failed to connect to server: {e}")
                await asyncio.sleep(5)  # Ждем 5 секунд перед попыткой повторного подключения

    async def send_message(self):
        await self.connect()  # Подключаемся к серверу перед отправкой сообщений
        if self.websocket:
            try:
                while True:
                    message = input("Enter message to send (type 'exit' to quit): ")
                    if message == 'exit':
                        break
                    await self.websocket.send(message)
                    response = await self.websocket.recv()
                    print(f"Received response from server: {response}")
            except websockets.exceptions.ConnectionClosed:
                print("Server connection closed, reconnecting...")
                await self.connect()  # Переподключаемся к серверу при разрыве соединения
        else:
            print("Not connected to server")


async def start(core: Core):
    manifest = {
        "name": "Плагин вебсокет сервера",
        "version": "0.1",
        "default_options": {
            "host": "localhost",
            "port": 8766,
        }
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    print('старте вебсокета клиента')
    host = manifest["options"]["host"]
    port = manifest["options"]["port"]
    client = WebSocketClient(f"ws://{host}:{port}")
    # asyncio.run(client.send_message())

    asyncio.run_coroutine_threadsafe(client.send_message(), asyncio.get_running_loop())


# async def run():
#     print('старте вебсокета клиента')
#     client = WebSocketClient("ws://localhost:8765")
#     asyncio.run(client.send_message())
