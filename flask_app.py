from flask import Flask, request
import logging
import json
from os import environ
from requests import get

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res: dict, req: dict):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу переводить слова. Напиши, "переведи <фраза>" или "язык <код_языка>"'
        sessionStorage[user_id] = {'language': 'en'}
        return
    language = get_language(req)
    translate = get_translate(req)
    if language is not None:
        if translate_text('кот', language) in ['The specified translation direction is not supported',
                                               'Invalid parameter: lang']:
            res['response']['text'] = 'Неверный код языка'
        else:
            res['response']['text'] = 'Язык успешно изменён'
            sessionStorage[user_id]['language'] = language
    elif translate is not None:
        res['response']['text'] = translate_text(translate, sessionStorage[user_id]['language'])
    else:
        res['response']['text'] = 'Я понимаю только фразы: "переведи <фраза>" и "язык <код_языка>"'


def translate_text(text: str, lang: str):
    result = get('https://translate.yandex.net/api/v1.5/tr.json/translate', {'key': 'trnsl.1.1.20200330T045422Z.88d6e713d66d9168.57a8fe547ee9d0c40b871e3d0ee9e5f59af7a1fa', 'text': text, 'lang': lang}).json()
    return result['text'][0] if result['code'] == 200 else result['message']


def get_translate(req: dict):
    if len(req['request']['command'].split()) > 1 and req['request']['command'].split()[0] == 'переведи':
        return ' '.join(req['request']['command'].split()[1:])


def get_language(req: dict):
    if len(req['request']['command'].split()) == 2 and req['request']['command'].split()[0] == 'язык':
        return req['request']['command'].split()[1]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(environ.get("PORT", 5000)))
