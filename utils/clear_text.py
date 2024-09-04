import re
import asyncio
import json
import os
import sys
from num2words import num2words
import logging


def parse_string(input_string, desired_mention):
    pattern = rf'@({desired_mention})\s+(.*)'  # Регулярное выражение с учетом конкретного упоминания
    match = re.match(pattern, input_string)
    if match:
        mention = match.group(1)  # Получаем упоминание (после символа @)
        message = match.group(2)  # Получаем текст обращения (после упоминания)
        return mention, message
    else:
        return None, None

def split_into_sentences(text):
    """Разбивает текст на предложения."""
    sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s')
    sentences = sentence_endings.split(text)
    return sentences


def merge_sentences(sentences, max_length):
    """Объединяет предложения в блоки заданной максимальной длины."""
    current_chunk = []
    current_length = 0
    chunks = []

    for sentence in sentences:
        if current_length + len(sentence) <= max_length:
            current_chunk.append(sentence)
            current_length += len(sentence)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def preprocess_text(text, max_length=800):
    """Предобрабатывает текст, разбивая его на блоки."""
    text = replace_numbers(text)
    sentences = split_into_sentences(text)
    chunks = merge_sentences(sentences, max_length)
    return chunks


def clean_text(text):
    """Форматирует текст, удаляя лишние пробелы и пустые строки."""
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()
    return text


def replace_numbers(text):
    """Заменяет числа в тексте на слова."""

    def replacer(match):
        return num2words(int(match.group()), lang='ru')

    return re.sub(r'\b\d+\b', replacer, text)