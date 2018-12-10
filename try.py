#coding: utf-8
#Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import random
from string import punctuation
from datetime import datetime, timedelta
from alice_scripts import Skill, request as r, say, suggest


# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }
        
    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

## Открытие и чтение таблицы стран 
def urlCountry():
    with open('countries.csv', 'r', encoding = 'utf-8') as f:
        f = f.readlines()
    countries4url = list(set(list(i.split(';')[-1].strip('\n') for i in f)))
    countries_ru = list(set(list(i.split(';')[0].lower().strip('\n') for i in f)))
    variants = []
    for c in countries4url:
        line_vars = []
        for line in f:
            if line.split(';')[-1].strip('\n') == c and line.split(';')[2].lower() not in line_vars:
                line_vars.append(line.split(';')[2].lower())
            if line.split(';')[0].lower().strip('\n') in countries_ru and line.split(';')[0].strip('\n').lower() in line_vars:
                line_vars.remove(line.split(';')[0].strip('\n').lower())
                line_vars.insert(0,line.split(';')[0].strip('\n').lower())
        variants.append({c:line_vars})
    return variants, countries_ru

global variants
variants, countries_ru = urlCountry()
all_countries = []
for i in variants:
    all_countries += [word.lower() for word in list(i.values())[0]]
all_countries = list(set(all_countries))

def greets(req):
    if req['session']['new'] == True:
        yield say('Привет! Этот навык поможет узнать о продуктах Ингосстраха. Выберите вид страхования',
                  'Здравствуйте! Я расскажу о видах страхования в Ингосстрахе. Что вас интересует?',
                  'Добрый день. Узнайте о видах страхования в Ингосстрахе. Что нужно застраховать?',
                  suggest('Путешествия', 'Автомобили', 'Здоровье и жизнь', 'Инвестиции и пенсия', 'Имущество'))
    else:
        yield say('Да-да, здесь все еще можно узнать о продуктах Ингосстраха. Какой вид страхования вас интересует?',
                  'И снова здравствуйте! Выберите вид страхования	',
                  'Не стесняйтесь! Что нужно застраховать?	',
                  suggest('Путешествия', 'Автомобили', 'Здоровье и жизнь', 'Инвестиции и пенсия', 'Имущество'))

    while True:
        if r.has_lemmas('путешествие', 'граница', 'рубеж'):
            return 'travel'
        if r.has_lemmas('машина', 'автомобиль', 'авто', 'каско', 'осаго'):
            return 'auto'
        if r.has_lemmas('здоровье', 'жизнь', 'медицинский'):
            return 'health'
        if r.has_lemmas('инвестиция', 'инвестирование', 'пенсия'):
            return 'invest'
        if r.has_lemmas('имущество', 'недвижимость', 'дом', 'квартира', 'дача'):
            return 'prop'
        
        yield say('Кажется, я вас не понимаю. Выберите один из продуктов, чтобы узнать больше.',
                  suggest('Путешествия', 'Автомобили', 'Здоровье и жизнь', 'Инвестиции и пенсия', 'Имущество'))
        
def products(req, res, profile):
    if profile['product'] == 'auto':
        yield say('Воспользуйтесь программами страхования транспортных средств и застрахуйте возможные риски, связанные с эксплуатацией автомобиля.',
                  suggest('Узнать больше','В начало'))

   
def handle_dialog(req, res):
    profile = {'product': (yield from greets(req))}
    greets(req)
    products(req, res, profile)
    
