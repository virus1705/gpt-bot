import json
import logging  # ������ ��� ����� �����
import time  # ������ ��� ������ �� ��������
from datetime import datetime  # ������ ��� ������ � ����� � ��������
import requests
# ����������� ��������� �� config-�����
from config import LOGS, IAM_TOKEN_PATH, FOLDER_ID_PATH, BOT_TOKEN_PATH

# ����������� ������ ����� � ����
logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# ��������� ������ iam_token
def create_new_token():
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {
        "Metadata-Flavor": "Google"
    }
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()  # ����������� �� ������ iam_token
            # ��������� ����� ��������� iam_token � �������� �������
            token_data['expires_at'] = time.time() + token_data['expires_in']
            # ���������� iam_token � ����
            with open(IAM_TOKEN_PATH, "w") as token_file:
                json.dump(token_data, token_file)
            logging.info("������� ����� iam_token")
        else:
            logging.error(f"������ ��������� iam_token. ������-���: {response.status_code}")
    except Exception as e:
        logging.error(f"������ ��������� iam_token: {e}")

# ������ iam_token � folder_id.txt �� �����
def get_creds():
    try:
        # ������ iam_token
        with open(IAM_TOKEN_PATH, 'r') as f:
            file_data = json.load(f)
            expiration = datetime.strptime(file_data["expires_at"][:26], "%Y-%m-%dT%H:%M:%S.%f")
        # ���� ���� �������� ����
        if expiration < datetime.now():
            logging.info("���� �������� iam_token ����")
            # �������� ����� iam_token
            create_new_token()
    except:
        # ���� ���-�� ����� �� ��� - �������� ����� iam_token
        create_new_token()

    # ������ iam_token
    with open(IAM_TOKEN_PATH, 'r') as f:
        file_data = json.load(f)
        iam_token = file_data["access_token"]

    # ������ folder_id.txt
    with open(FOLDER_ID_PATH, 'r') as f:
        folder_id = f.read().strip()

    return iam_token, folder_id

# ������ bot_token.txt �� �����
def get_bot_token():
    with open(BOT_TOKEN_PATH, 'r') as f:
        return f.read().strip()
