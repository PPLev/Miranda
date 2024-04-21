import asyncio
import logging
import os
import time

import sounddevice
import torch

import packages
from core import Core
from utils.custom_filters import levenshtein_filter

logger = logging.getLogger("root")
core = Core()

silero_model = None
is_mute = False
model_settings = {}
output_device_id = None

audio_queue = asyncio.Queue()


async def start(core: Core):
    manifest = {
        "name": "Плагин генерации речи с помощью silero",
        "version": "1.1",
        "default_options": {
            "model_settings": {
                "model_path": "",
                "model_name": "silero.pt",
                "model_url": "https://models.silero.ai/models/tts/ru/v4_ru.pt"
            },
            "output_device_id": None,
        },
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    global model_settings, output_device_id
    model_settings = manifest["options"]["model_settings"]
    output_device_id = manifest["options"]["output_device_id"]
    asyncio.run_coroutine_threadsafe(play(), asyncio.get_running_loop())


async def play():
    while True:

        if audio_queue.empty():
            await asyncio.sleep(0)
        else:
            core.sound_playing = True
            logger.info(f"Статус записи: {core.sound_playing}")
            audio = await audio_queue.get()
            sounddevice.play(audio, samplerate=24000)
            sounddevice.wait()
            core.sound_playing = False
            logger.info(f"Статус записи: {core.sound_playing}")
            #TODO: асинхронн ждем пока идет овучка


async def _say_silero(core: Core, output_str):
    global silero_model, model_settings
    if is_mute:
        return
    if silero_model is None:  # Подгружаем модель если не подгрузили ранее
        logger.debug("Загрузка модели силеро")
        # Если нет файла модели - скачиваем
        if not os.path.isfile(model_settings["model_path"] + model_settings["model_name"]):
            logger.debug("Скачивание модели silero")
            torch.hub.download_url_to_file(
                model_settings["model_url"], model_settings["model_path"] + model_settings["model_name"]
            )

        silero_model = torch.package.PackageImporter(
            model_settings["model_path"] + model_settings["model_name"]
        ).load_pickle("tts_models", "model")
        device = torch.device("cpu")
        silero_model.to(device)
        logger.debug("Загрузка модели силеро завершена")

    if not output_str:
        return

    say_str = output_str.replace("…", "...")

    logger.info(f"Генерация аудио для '{say_str}'")
    audio = silero_model.apply_tts(text=say_str,
                                   speaker="xenia",
                                   sample_rate=24000)

    if output_device_id:
        sounddevice.default.device = (None, output_device_id)

    await audio_queue.put(audio)
    # sounddevice.play(audio, samplerate=24000)
    # TODO: Сделать блокировку распознавания при воспроизведении
    # sounddevice.wait()


@core.on_output.register()
async def say_silero(package: packages.TextPackage):
    await _say_silero(core, package.input_text)
    if package.text:
        await _say_silero(core, package.text)


@core.on_input.register(levenshtein_filter("без звука", min_ratio=85))
async def mute(package):
    global is_mute
    is_mute = not is_mute
