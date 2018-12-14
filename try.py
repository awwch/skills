#coding: utf-8
#Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import random
import re
from string import punctuation
from datetime import datetime, timedelta
from alice_scripts import say

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
            try:
                if line.split(';')[-1].strip('\n') == c and line.split(';')[2].lower() not in line_vars:
                    line_vars.append(line.split(';')[2].lower())
                if line.split(';')[0].lower().strip('\n') in countries_ru and line.split(';')[0].strip('\n').lower() in line_vars:
                    line_vars.remove(line.split(';')[0].strip('\n').lower())
                    line_vars.insert(0,line.split(';')[0].strip('\n').lower())
            except:
                continue
        variants.append({c:line_vars})
    return variants, countries_ru

global variants
variants, countries_ru = urlCountry()
all_countries = []
for i in variants:
    all_countries += [word.lower() for word in list(i.values())[0]]
all_countries = list(set(all_countries))

def greets(req,res):
    global start_buttons
    start_buttons = [{"title": "Путешествия","hide": True},
               {"title": "Автомобили","hide": True},
               {"title": "Здоровье и жизнь","hide": True},
               {"title": "Инвестиции и пенсия","hide": True},
               {"title": "Имущество","hide": True}]
    res['response']['buttons'] = start_buttons

    if req['session']['new'] == True:
        res['response']['text'] = random.choice(['Привет! Этот навык поможет \
           рассчитать стоимость страховки для путешественников, а также узнать\
           о других страховых продуктах Ингосстраха. Выберите вид страхования.\
           Чтобы посчитать стоимость туристической страховки, выберите "Путешествия"',
           'Здравствуйте! Я помогу рассчитать стоимость страховки для путешественников \
           и расскажу о видах страхования в Ингосстрахе. Что вас интересует?',
           'Добрый день. Здесь можно рассчитать стоимость туристической страховки \
           и узнать о других видах страхования в Ингосстрахе. Что нужно застраховать?'])
        return
    else:
        res['response']['text'] = random.choice(['Да-да, здесь все еще можно рассчитать \
           стоимость туристической страховки и узнать о продуктах Ингосстраха. \
           Какой вид страхования вас интересует?',
           'И снова здравствуйте! Выберите "Путешествия" для расчета стоимости \
           полиса путешественника. Выберите другие продукты, чтобы узнать о них больше.',
           'Не стесняйтесь! Что нужно застраховать? Выберите "Путешествия" для \
           расчета стоимости полиса путешественника. Выберите другие продукты, \
           чтобы узнать о них больше.'])
        return

def products(req, res):
    if 'авто' in req['request']['original_utterance'].lower() or 'машин' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Воспользуйтесь программами страхования транспортных \
        средств и застрахуйте возможные риски, связанные с эксплуатацией автомобиля.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/auto/","hide": True}, 
           {"title": "В начало","hide": True}]
        return
    if 'здоров' in req['request']['original_utterance'].lower() or 'жизн' in req['request']['original_utterance'].lower() or 'медиц' in req['request']['original_utterance'].lower() or 'спор' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Жизнь и здоровье - самые ценные ресурсы любого \
        человека. Мы предлагаем разные продукты в этой сфере: от страхования от \
        несчастного случая на соревнованиях до ДМС для получения качественной медицинской помощи.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/health_life/","hide": True},
           {"title": "В начало","hide": True}]
        return
    if 'инвест' in req['request']['original_utterance'].lower() or 'пенси' in req['request']['original_utterance'].lower() or 'пожил' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Мы предлагаем не только программы пенсионного \
        страхования, но и различные инструменты для инвестирования.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/pension_investment/","hide": True},
           {"title": "В начало","hide": True}]
        return
    if 'имущ' in req['request']['original_utterance'].lower() or 'недвиж' in req['request']['original_utterance'].lower() or 'дом' in req['request']['original_utterance'].lower() or 'квартир' in req['request']['original_utterance'].lower() or 'дача' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Страхование имущества — дома, квартиры или \
        дачи — это возможность защитить имущество и уберечь себя от непредвиденных \
        финансовых затрат.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/property/","hide": True},
           {"title": "В начало","hide": True}]
        return

class vzr:
    countries = []
    countries_rus = []
    dates = {}
    ages = ''
    
    def chooseCountry(req, res):
        vzr.countries.clear()
        vzr.countries_rus.clear()
        global country_buttons
        country_buttons = [{"title": 'Шенген', "hide": True},
           {"title": "Италия", "hide": True},
           {"title": "Испания", "hide": True},
           {"title": "В начало","hide": True}]
        res['response']['buttons'] = country_buttons
        res['response']['text'] = random.choice(['В каких странах вы собираетесь \
           пользоваться страховкой? Укажите первую страну посещения.',
          'Для каких стран вам нужна страховка? Назовите первую страну для посещения.'])
    
    def nextCountry(req, res):
        global fine_countries
        global all_countries
        global country_buttons
        fine_countries = list(set(vzr.countries_rus))
        vzr.countries = list(set(vzr.countries))
        res['response']['buttons'] = country_buttons
        res['response']['text'] = '''Ваш выбор: {}. 
        Укажите следующую страну вашего путешествия или перейдите на следующий шаг.'''.format(str(fine_countries).strip("\['\]").replace("'",'').upper())
        if {"title": "Следующий шаг", "hide": True} not in res['response']['buttons']:
                res['response']['buttons'].insert(0,{"title": "Следующий шаг", "hide": True})
        if {"title": "Изменить список стран", "hide": True} not in res['response']['buttons']:
            res['response']['buttons'].insert(1,{"title": "Изменить список стран", "hide": True})

vzr.countries = []
vzr.countries_rus = []
vzr.dates = {}
vzr.ages = ''
profile = ''
def handle_dialog(req, res):
    global profile
    global start_buttons
    global country_buttons
    product = req['request']['original_utterance'].lower()
    
    if re.match(r'помощ|помог|что ты умеешь',product):
        res['response']['text'] = 'Я могу помочь вам рассчитать стоимость страховки \
        для путешествий, а также рассказать о других видах страхования в Ингосстрахе. \
        Чтобы рассчитать стоимость полиса для путешественника, выберите "Путешествия". \
        Для расчета нужно знать страны поездки, даты, количество и возраст путешественников. \
        Чтобы ознакомиться с другими продуктами, выберите их из списка ниже.'
        res['response']['buttons'] = start_buttons
        return
        
    while not re.match(r'путешест|грани|рубеж|авто|машин|каско|осаго|жизн|здоров|медиц|спор|инвест|пенси|пожил|имущ|недвиж|квартир|дом|дач',product) or profile == 'travel':
        if req['session']['new'] != True:
            res['response']['text'] = 'Кажется, я вас не понимаю. Выберите "Путешествия" \
            для расчета стоимости туристической страховки, либо другой страховой продукт, \
            чтобы узнать о нем больше.'
            res['response']['buttons'] = start_buttons
        if req['session']['new'] == True or 'нача' in product or 'начн'in product:
            greets(req,res)
            return
        product = req['request']['original_utterance'].lower()
    
    if re.match(r'авто|машин|каско|осаго|жизн|здоров|медиц|спор|инвест|пенси|пожил|имущ|недвиж|квартир|дом|дач',product):
        products(req, res)
        return

    if 'путешест' in req['request']['original_utterance'].lower() or 'границ' in req['request']['original_utterance'].lower() or 'рубеж' in req['request']['original_utterance'].lower():
        profile = 'travel'
        vzr.chooseCountry(req,res)
        return

    if req['request']['original_utterance'].lower() in all_countries:
    #while req['request']['original_utterance'].lower() in all_countries and req['request']['original_utterance'].lower() != '':
        for v in variants:
            if req['request']['original_utterance'].lower() in list(v.values())[0]:
                chozen_country = list(v.values())[0][0]
                vzr.countries.append(list(v.keys())[0])
                vzr.countries_rus.append(chozen_country)
        vzr.nextCountry(req, res)
        return
