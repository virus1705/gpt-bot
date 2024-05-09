BOT_TOKEN_PATH = "creds/bot_token.txt"
IAM_TOKEN_PATH = "creds/iam-token.txt"
FOLDER_ID_PATH = 'creds/folder_id.txt'

MAX_USERS = 3  # ������������ ���-�� �������������
MAX_GPT_TOKENS = 120  # ������������ ���-�� ������� � ������ GPT
COUNT_LAST_MSG = 4  # ���-�� ��������� ��������� �� �������

# ������ ��� ������������
MAX_USER_STT_BLOCKS = 10  # 10 �����������
MAX_USER_TTS_SYMBOLS = 5_000  # 5 000 ��������
MAX_USER_GPT_TOKENS = 2_000  # 2 000 �������

LOGS = 'logs.txt'  # ���� ��� �����
DB_FILE = 'messages.db'  # ���� ��� ���� ������
SYSTEM_PROMPT = [{'role': 'system', 'text': '�� ������� ����������. ������� � ������������� �� "��" � ��������� ����. '
                                            '����������� ������. �� �������� ������������, ��� �� ������ � ������. '
                                            '��������� ��������'}]  # ������ � ��������� �������
WHITE_LIST = ["yagit0"]