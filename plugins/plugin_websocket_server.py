import asyncio
import json
import os
import sys
import websockets

from core import Core
import logging

logger = logging.getLogger("root")

core = Core()


async def start(core: Core):
    manifest = {
        "name": "Плагин вебсокет сервера",
        "version": "0.1",
        "default_options": {
            "host": "localhost",
            "port": 8765,
        }
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    host = manifest["options"]["host"]
    port = manifest["options"]["port"]

    core.ws_server = WebSocketServer(host, port)

    asyncio.run_coroutine_threadsafe(core.ws_server.start(), asyncio.get_running_loop())


class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.settings = {}
        self.clients = set()
        self.websocket = None  # Добавляем атрибут для объекта WebSocket

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        self.websocket = websocket  # Устанавливаем атрибут self.websocket
        try:
            async for message in websocket:
                print(f"Received message from client: {message}")
                # Парсим сообщение от клиента
                data = json.loads(message)
                if 'action' in data:
                    action = data['action']
                    if action == 'get_settings':
                        # Отправляем текущие настройки клиенту
                        await self.send_to_client(json.dumps(core.plugin_manifests))
                    elif action == 'update_settings':
                        # Обновляем настройки
                        if 'settings' in data:
                            new_settings = data['settings']
                            self.settings.update(new_settings)
                            print("Settings updated:", self.settings)
                            # Отправляем подтверждение клиенту
                            await self.send_to_client({"message": "Settings updated successfully"})
        finally:
            self.clients.remove(websocket)

    async def send_to_client(self, message):
        if self.websocket:  # Проверяем, что есть активное соединение
            try:
                await self.websocket.send(json.dumps(message))  # Используем self.websocket
            except Exception as e:
                print(f"Failed to send message to client: {e}")
        else:
            print("No active WebSocket connection to send message.")

    async def start(self):
        server = await websockets.serve(self.handle_client, self.host, self.port, ping_timeout=None)
        print(f"WebSocket server started at ws://{self.host}:{self.port}")
        if self.websocket:
            for value in core.plugin_manifests.values():
                print(value)
            await self.send_to_client(value)
        else:
            print("No active WebSocket connection to send message.")
        await server.wait_closed()
