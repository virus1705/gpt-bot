MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

HOME_DIR = '/home/student/gpt-bot'  # путь к папке с проектом
LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/messages.db'  # файл для базы данных

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10
MAX_USER_TTS_SYMBOLS = 5_000
MAX_USER_GPT_TOKENS = 2_000
MAX_TTS_SYMBOLS = 500

LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]
WHITE_LIST = ["yagit0"]