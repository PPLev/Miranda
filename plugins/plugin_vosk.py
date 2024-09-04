import asyncio
import json
import os
import sys
import wave

import soundfile
import vosk
import pyaudio
import logging

from core import Core
import packages

logger = logging.getLogger("root")

core = Core()

model_settings = {}
input_device_id = None
vosk_model = None


async def all_ok(package: packages.TextPackage):
    await package.core.on_output(packages.TextPackage(package.text, package.core, packages.NULL_HOOK))


def load_model():
    global vosk_model
    vosk_model = vosk.Model(model_settings["model_path"] + model_settings["model_name"])  # Подгружаем модель


def recognize_file(file):
    data, samplerate = soundfile.read(file)
    soundfile.write(file, data, samplerate)

    wf = wave.open(file, "rb")

    if vosk_model is None:
        load_model()

    rec = vosk.KaldiRecognizer(vosk_model, 44100)
    rec.SetWords(True)
    rec.SetPartialWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    if "text" in (recognized := json.loads(rec.FinalResult())):
        return recognized["text"]

    return "Не распознано("


async def run_vosk():
    """
    Распознование библиотекой воск
    """
    import sounddevice
    #:TODO настройка устройства вывода потом переписать
    # sounddevice.default.device = (1, None)
    # dev_out = sounddevice.query_devices(kind="input")
    # print(dev_out)
    # print(sounddevice.check_output_settings())

    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=44100,
                     input=True,
                     input_device_index=input_device_id,
                     frames_per_buffer=8000)

    if not os.path.isdir(model_settings["model_path"] + model_settings["model_name"]):
        logger.warning("Папка модели воск не найдена\n"
                       "Please download a model for your language from https://alphacephei.com/vosk/models")
        sys.exit(0)

    if not vosk_model:
        load_model()

    rec = vosk.KaldiRecognizer(vosk_model, 44100)

    logger.info("Запуск распознователя речи vosk вход в цикл")
    logger.info(f"{input_device_id}")

    while True:
        await asyncio.sleep(0)

        if not core.sound_playing:
            data = stream.read(8000)

            if rec.AcceptWaveform(data):
                recognized_data = rec.Result()
                recognized_data = json.loads(recognized_data)
                voice_input_str = recognized_data["text"]
                if voice_input_str != "" and voice_input_str is not None:
                    logger.info(f"Распознано Vosk: '{voice_input_str}'")
                    package = packages.TextPackage(voice_input_str, core, all_ok)
                    await core.on_input(package=package)


async def start(core: Core):
    manifest = {
        "name": "Плагин распознования речи с помощью воск",
        "version": "1.0",

        "default_options": {
            "model_settings": {
                "model_path": "",
                "model_name": "model"
            },
            "input_device_id": None
        },
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    global model_settings, input_device_id
    model_settings = manifest["options"]["model_settings"]
    input_device_id = manifest["options"]["input_device_id"]

    asyncio.run_coroutine_threadsafe(run_vosk(), asyncio.get_running_loop())

    core.recognize_file = recognize_file
    core.sound_playing = False
