import os
import json

from core import Core, F

core = Core()


@core.on_input.register(F.startswith("запомни"))
async def in_notise(package):
    prompt = f"""
Тебе надо сформировать единицу знания из следующего запроса: "{package.input_text}"

Пример: "запомни что я положил ручку на стол"
Ответ: "Ручка лежит на столе"
    """

    answer = await core.gpt.ask(prompt)
    print(answer)
    # TODO: Изменить: добавить выбор папки и все упаковать в json + сделать метод в бд
