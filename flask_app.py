import json
import logging
from os import environ

from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
animals = ['слона', 'кролика']

sessionStorage = {}
sessionAnimal = {}


@app.route('/', methods=['GET'])
@app.route('/test', methods=['GET'])
def test_page():
    return 'Server is ok. have a nice day'


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {'end_session': False}
    }
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        sessionAnimal[user_id] = 0
        res['response']['text'] = f'Привет! Купи {animals[sessionAnimal[user_id]]}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in ['ладно', 'куплю', 'покупаю', 'хорошо', 'я покупаю', 'я куплю']:
        last = sessionAnimal[user_id] + 1 == len(animals)
        res['response']['text'] = f'{animals[sessionAnimal[user_id]].capitalize()} можно найти на Яндекс.Маркете!' + (f' А купи ещё {animals[sessionAnimal[user_id] + 1]}!' if not last else '')
        sessionAnimal[user_id] += 1
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        if last:
            res['response']['end_session'] = True
        return

    res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи {animals[sessionAnimal[user_id]]}!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={animals[sessionAnimal[user_id]]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    # https://yandex-alice-luceum.herokuapp.com
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
