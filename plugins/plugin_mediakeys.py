from core import Core
import pyautogui


async def start(core: Core):
    manifest = {
        "name": "Плагин медиаклавиш",
        "version": "1.0",
        "require_online": False,
        "is_active": True,

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    pass




def press_hotkey_pyautogui(hotkey: str):
    pyautogui.hotkey(hotkey)
