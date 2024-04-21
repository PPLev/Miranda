from fuzzywuzzy import fuzz

from core import F


def text_comparison(str1, str2, min_ratio=85) -> bool:
    """
    Проверка схожести строк в процентах, основано на расстоянии Левенштейна
    :param str1:
    :param str2:
    :param min_ratio: минимальный процент для проверки
    :return: bool
    """
    if fuzz.token_sort_ratio(str1, str2) > min_ratio:
        return True
    if str1 in str2:
        return True
    return False


def levenshtein_filter(text, min_ratio=80):
    return F.func(lambda input_text: text_comparison(input_text, text, min_ratio))
