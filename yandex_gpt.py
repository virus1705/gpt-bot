import requests
import logging
from config import LOGS, MAX_GPT_TOKENS, SYSTEM_PROMPT
from creds import get_creds  # ìîäóëü äëÿ ïîëó÷åíèÿ òîêåíîâ

IAM_TOKEN, FOLDER_ID = get_creds()  # ïîëó÷àåì iam_token è folder_id.txt èç ôàéëîâ

logging.basicConfig(filename=LOGS,
                    level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
                    filemode="w")

# ïîäñ÷èòûâàåì êîëè÷åñòâî òîêåíîâ â ñîîáùåíèÿõ
def count_gpt_tokens(messages):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "messages": messages
    }
    try:
        return len(requests.post(url=url, json=data, headers=headers).json()['tokens'])
    except Exception as e:
        logging.error(e)  # åñëè îøèáêà - çàïèñûâàåì å¸ â ëîãè
        return 0

# çàïðîñ ê GPT
def ask_gpt(messages):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": MAX_GPT_TOKENS
        },
        "messages": SYSTEM_PROMPT + messages  # äîáàâëÿåì ê ñèñòåìíîìó ñîîáùåíèþ ïðåäûäóùèå ñîîáùåíèÿ
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        # ïðîâåðÿåì ñòàòóñ êîä
        if response.status_code != 200:
            return False, f"Îøèáêà GPT. Ñòàòóñ-êîä: {response.status_code}", None
        answer = response.json()['result']['alternatives'][0]['message']['text']
        tokens_in_answer = count_gpt_tokens([{'role': 'assistant', 'text': answer}])
        return True, answer, tokens_in_answer
    except Exception as e:
        logging.error(e)  # åñëè îøèáêà - çàïèñûâàåì å¸ â ëîãè
        return False, "Îøèáêà ïðè îáðàùåíèè ê GPT",  None
