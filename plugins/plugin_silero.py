import asyncio
import logging
import os
import time
import sounddevice
import torch
import soundfile as sf

import requests
from urllib.parse import urlencode

import packages
from core import Core
from utils.clear_text import preprocess_text, clean_text
from utils.custom_filters import levenshtein_filter

logger = logging.getLogger(__name__)
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
            sounddevice.play(audio, samplerate=48000)
            sounddevice.wait()
            time.sleep(2)
            core.sound_playing = False
            logger.info(f"Статус записи: {core.sound_playing}")
            # TODO: асинхронн ждем пока идет овучка


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
    # cleaned_text = clean_text(say_str)
    # max_length = 900  # Установите предел символов для каждого блока
    # chunks = preprocess_text(cleaned_text, max_length)

    # for i, chunk in enumerate(chunks):
    logger.info(f"Генерация аудио для '{say_str}'")
    audio = silero_model.apply_tts(text=say_str,
                                   speaker="xenia",
                                   sample_rate=48000)
    if output_device_id:
        sounddevice.default.device = (None, output_device_id)
    await audio_queue.put(audio)
    # TODO: Сделать блокировку распознавания при воспроизведении


async def request_audio(core: Core, output_str):
    base_url = 'http://192.168.1.50:3001/generate'
    logger.error("TETST")

    # Параметры запроса
    speaker = 'xenia'
    sample_rate = 48000
    pitch = 50
    rate = 50

    say_str = output_str.replace("…", "...")

    cleaned_text = clean_text(say_str)
    max_length = 800  # Установите предел символов для каждого блока
    chunks = preprocess_text(cleaned_text, max_length)

    for i, chunk in enumerate(chunks):

        # Генерация URL с параметрами
        url = generate_url(base_url, chunk, speaker, sample_rate, pitch, rate)

        # Отправка GET-запроса
        response = requests.get(url)

        # Проверка статуса ответа
        if response.status_code == 200:
            logger.info('Запрос успешно выполнен!')

            # Сохранение аудиофайла
            file_name = f"audio/output_audio_{int(time.time())}.wav"
            with open(file_name, 'wb') as audio_file:
                audio_file.write(response.content)

            logger.info(f'Аудиофайл успешно сохранен как {file_name}')

            # Загрузка и воспроизведение аудиофайла
            audio_data, samplerate = sf.read(file_name, dtype='float32')
            await audio_queue.put(audio_data)
        else:
            logger.error(f'Ошибка выполнения запроса на сервер : {response.status_code}')


def generate_url(base_url, text, speaker, sample_rate, pitch, rate):
    params = {
        'text': text,
        'speaker': speaker,
        'sample_rate': sample_rate,
        'pitch': pitch,
        'rate': rate
    }
    url = f"{base_url}?{urlencode(params)}"
    return url


@core.on_output.register()
async def say_silero(package: packages.TextPackage):
    await _say_silero(core, package.input_text)
    if package.text:
        await _say_silero(core, package.text)


# @core.on_output.register()
# async def request_audio_handler(package: packages.TextPackage):
#     await request_audio(core, package.input_text)
#     if package.text:
#         await request_audio(core, package.text)


# @core.on_input.register(levenshtein_filter("без звука", min_ratio=85))
# async def mute(package):
#     global is_mute
#     is_mute = not is_mute




