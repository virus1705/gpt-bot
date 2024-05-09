import logging  # ������ ��� ����� �����
import math  # �������������� ������ ��� ����������
# ����������� ��������� �� config �����
from config import LOGS, MAX_USERS, MAX_USER_GPT_TOKENS, MAX_USER_TTS_SYMBOLS, MAX_USER_STT_BLOCKS
# ����������� ������� ��� ������ � ��
from database import count_users, count_all_limits, count_all_symbol, count_all_blocks
# ����������� ������� ��� �������� ������� � ������ ���������
from yandex_gpt import count_gpt_tokens

# ����������� ������ ����� � ����
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# �������� ���������� ���������� �������������, ����� ������ ������������
def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return None, "������ ��� ������ � ��"
    if count > MAX_USERS:
        return None, "��������� ������������ ���������� �������������"
    return True, ""

# ���������, �� �������� �� ������������ ������ �� ������� � GPT
def is_gpt_token_limit(messages, total_spent_tokens):
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f"�������� ����� ����� GPT-������� {MAX_USER_GPT_TOKENS}"
    return all_tokens, ""

# ���������, �� �������� �� ������������ ������ �� �������������� ����� � �����
def is_stt_block_limit(message, duration):
    user_id = message.from_user.id

    logging.info('��������� ������� � ����������')
    audio_blocks = math.ceil(duration / 15) # ��������� � ������� �������
    # ������� �� �� ��� �������� ���� ����������� ������������� �����������
    all_blocks = count_all_blocks(user_id) + audio_blocks

    logging.info('���������, ��� ����� ������ ������ 30 ������')
    if duration >= 30:
        return None

    logging.info('���������� all_blocks � ����������� ��������� ������������ �����������')
    if all_blocks >= MAX_USER_STT_BLOCKS:
        return None

    return audio_blocks

# ���������, �� �������� �� ������������ ������ �� �������������� ������ � �����
def is_tts_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    # ������� �� �� ��� �������� ���� ����������� ������������� ��������
    all_symbols = count_all_symbol(user_id) + text_symbols

    logging.info('���������� all_symbols � ����������� ��������� ������������ ��������')
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"�������� ����� ����� SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. ������������: {all_symbols} ��������. ��������: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        return None

    logging.info('���������� ���������� �������� � ������ � ������������ ����������� �������� � ������')
    if text_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"�������� ����� SpeechKit TTS �� ������ {MAX_USER_TTS_SYMBOLS}, � ��������� {text_symbols} ��������"
        return None
    return len(text)