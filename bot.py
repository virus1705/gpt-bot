from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from SpeechKit import *
from validators import *
from yandex_gpt import ask_gpt
from config import LOGS, COUNT_LAST_MSG, WHITE_LIST
from creds import get_bot_token
from database import create_database, add_message, select_n_last_messages, insert_row
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="w"
)

bot = TeleBot(get_bot_token())
create_database()

def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    logging.info("Запуск бота.")
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот-помощник, способный отвечать на голосовые и текстовые сообщения.\n"
                          f"Если возникают трудности в использовании бота нажмите на кнопку help",
                     reply_markup=create_keyboard(["/tts", "/stt", '/help']))



@bot.message_handler(commands=['help'])
def support(message):
    logging.info("Открытие help.")
    if message.from_user.username in WHITE_LIST:
        keyboard = ["/tts", "/stt", "/debug"]
        text = ("Для обращения к GPT отправь голосовое или текстовое сообщение."
                "Чтобы перевести текст в речь: нажми на tts."
                "Чтобы перевести речь в текст: нажми на stt."
                "Чтобы открыть логи: нажми на debug.")
    else:
        keyboard = ["/tts", "/stt"]
        text = ("Для обращения к GPT отправь голосовое или текстовое сообщение."
                "Чтобы перевести текст в речь: нажми на tts."
                "Чтобы перевести речь в текст: нажми на stt.")
    bot.send_message(message.from_user.id, text=text, reply_markup=create_keyboard(keyboard))


@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщеним текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)

def tts(message):
    user_id = message.from_user.id
    text = message.text

    logging.info('Проверка, что сообщение действительно текстовое')
    if message.content_type != 'text':
        bot.send_message(user_id, 'Отправь текстовое сообщение')
        return

    logging.info('Считаем символы в тексте и проверяем сумму потраченных символов')
    text_symbol = is_tts_symbol_limit(message, text)
    if text_symbol is None:
        return

    logging.info('Записываем сообщение и кол-во символов в БД')
    insert_row(user_id, text, "tts_symbols", text_symbol)

    logging.info('Получаем статус и содержимое ответа от SpeechKit')
    status, content = text_to_speech(text)

    # Если статус True - отправляем голосовое сообщение, иначе - сообщение об ошибке
    if status:
        logging.info('Отправка голосового сообщения')
        bot.send_voice(user_id, content)
    else:
        logging.info('Отправка сообщения об ошибке')
        bot.send_message(user_id, content)





# Обрабатываем команду /stt
@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt)


# Переводим голосовое сообщение в текст после команды stt
def stt(message):
    user_id = message.from_user.id

    logging.info('Проверка, что сообщение действительно голосовое')
    if not message.voice:
        return

    logging.info('Считаем аудиоблоки и проверяем сумму потраченных аудиоблоков')
    stt_blocks = is_stt_block_limit(message, message.voice.duration)
    if not stt_blocks:
        return

    file_id = message.voice.file_id
    logging.info('получаем id голосового сообщения')
    file_info = bot.get_file(file_id)
    logging.info('получаем информацию о голосовом сообщении')
    file = bot.download_file(file_info.file_path)
    logging.info('скачиваем голосовое сообщение')

    logging.info('Получаем статус и содержимое ответа от SpeechKit')
    status, text = speech_to_text(file)  # преобразовываем голосовое сообщение в текст

    # Если статус True - отправляем текст сообщения и сохраняем в БД, иначе - сообщение об ошибке
    if status:
        logging.info('Записываем сообщение и кол-во аудиоблоков в БД')
        insert_row(user_id, text, 'stt_blocks', stt_blocks)
        bot.send_message(user_id, text, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, text)



@bot.message_handler(commands=['debug'])
def debug(message):
    logging.info("Открытие файла с логами.")
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


# Декоратор для обработки голосовых сообщений, полученных ботом
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        user_id = message.from_user.id

        logging.info('Проверка на максимальное количество пользователей')
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        logging.info('Проверка на доступность аудиоблоков')
        stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        logging.info('Обработка голосового сообщения')
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

        logging.info('Запись в БД')
        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

        logging.info('Проверка на доступность GPT-токенов')
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        logging.info('Запрос к GPT и обработка ответа')
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        logging.info('Проверка на лимит символов для SpeechKit')
        tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)

        logging.info('Запись ответа GPT в БД')
        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if error_message:
            bot.send_message(user_id, error_message)
            return

        logging.info('Преобразование ответа в аудио и отправка')
        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")


# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        logging.info('ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)')
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)  # мест нет =(
            return

        logging.info('БД: добавляем сообщение пользователя и его роль в базу данных')
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        logging.info('ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов')
        logging.info('получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов')
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        logging.info('получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя')
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            logging.info('уведомляем пользователя и прекращаем выполнение функции')
            bot.send_message(user_id, error_message)
            return

        logging.info('GPT: отправляем запрос к GPT')
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        logging.info('GPT: обрабатываем ответ от GPT')
        if not status_gpt:
            logging.info('уведомляем пользователя и прекращаем выполнение функции')
            bot.send_message(user_id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        logging.info('БД: добавляем ответ GPT и потраченные токены в базу данных')
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


# обрабатываем все остальные типы сообщений
@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")

bot.polling()
