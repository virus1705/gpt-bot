import requests
from creds import get_creds  # модуль для получения токенов

IAM_TOKEN, FOLDER_ID = get_creds()  # получаем iam_token и folder_id.txt из файлов
def text_to_speech(text: str):
    # Ссылка, токен и Folder_id для Yandex SpeechKit
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    iam_token = IAM_TOKEN
    folder_id = FOLDER_ID

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',  # язык текста - русский
        'voice': 'filipp',  # голос Филиппа
        'folderId': folder_id,
    }
    # Выполняем запрос
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return True, response.content  # Возвращаем голосовое сообщение
    else:
        return False, "При запросе в SpeechKit возникла ошибка"


def speech_to_text(data):
    iam_token = IAM_TOKEN
    folder_id = FOLDER_ID

    # Указываем параметры запроса
    params = "&".join([
        "topic=general",
        f"folderId={folder_id}",
        "lang=ru-RU"
    ])

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}"

    # Выполняем запрос
    response = requests.post(url, headers=headers, data=data)

    # Читаем json в словарь
    decoded_data = response.json()
    # Проверяем, не произошла ли ошибка при запросе
    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")  # Возвращаем статус и текст из аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка"