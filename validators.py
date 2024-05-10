import logging  # модуль для сбора логов
import math  # математический модуль для округления
# подтягиваем константы из config файла
from config import LOGS, MAX_USERS, MAX_USER_GPT_TOKENS, MAX_USER_TTS_SYMBOLS, MAX_USER_STT_BLOCKS
# подтягиваем функции для работы с БД
from database import count_users, count_all_limits, count_all_symbol, count_all_blocks
# подтягиваем функцию для подсчета токенов в списке сообщений
from yandex_gpt import count_gpt_tokens

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# получаем количество уникальных пользователей, кроме самого пользователя
def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return None, "Ошибка при работе с БД"
    if count > MAX_USERS:
        return None, "Превышено максимальное количество пользователей"
    return True, ""

# проверяем, не превысил ли пользователь лимиты на общение с GPT
def is_gpt_token_limit(messages, total_spent_tokens):
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
    return all_tokens, ""

# проверяем, не превысил ли пользователь лимиты на преобразование аудио в текст
def is_stt_block_limit(message, duration):
    user_id = message.from_user.id

    logging.info('Переводим секунды в аудиоблоки')
    audio_blocks = math.ceil(duration / 15) # округляем в большую сторону
    # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
    all_blocks = count_all_blocks(user_id) + audio_blocks

    logging.info('Проверяем, что аудио длится меньше 30 секунд')
    if duration >= 30:
        return None

    logging.info('Сравниваем all_blocks с количеством доступных пользователю аудиоблоков')
    if all_blocks >= MAX_USER_STT_BLOCKS:
        return None

    return audio_blocks

# проверяем, не превысил ли пользователь лимиты на преобразование текста в аудио
def is_tts_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    logging.info('Сравниваем all_symbols с количеством доступных пользователю символов')
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        return None

    logging.info('Сравниваем количество символов в тексте с максимальным количеством символов в тексте')
    if text_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_USER_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        return None
    return len(text)
