BOT_TOKEN_PATH = "creds/bot_token.txt"
IAM_TOKEN_PATH = "creds/iam-token.txt"
FOLDER_ID_PATH = 'creds/folder_id.txt'

MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 5_000  # 5 000 символов
MAX_USER_GPT_TOKENS = 2_000  # 2 000 токенов

LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': "You're a fun conversationalist. Communicate in Russian with the user on 'you' and use humor."
                                            "Maintain the dialog. Don't explain to the user what you can and can do."
                                            "Play the man."}]
WHITE_LIST = ["yagit0"]
