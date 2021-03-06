#coding: utf-8
#Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import random
import re
from datetime import datetime, timedelta
from string import punctuation

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


#logging.basicConfig(filename="sample.log", filemode="a", level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}
#counter = 0
# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
#    global counter
    
    logging.info('Request: %r', request.json)
    
#    f_obj = open('update.log', 'a', encoding='utf-8')
#    logStr = str(logging.info('Request: %r', request.json))
#    string = str(datetime.now())[0:19] + ': ' + logStr + '\n'
#    f_obj.write(string)
#    f_obj.close()
    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }
    
#    session_id = response['session']['session_id']
#    sessionStorage.append(session_id)
        
    handle_dialog(request.json, response)
    logging.info('Response: %r', response)
    
#    f_obj = open('update.log', 'a', encoding='utf-8')
#    logStr = str(logging.info('Response: %r', response))
#    string = str(datetime.now())[0:19] + ': ' + logStr + '\n'
#    f_obj.write(string)
#    f_obj.close()
        
    return json.dumps(
            response,
            ensure_ascii=False,
            indent=2
        )
    
#    counter += 1

# Основные функции диалога
    
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
            #print(f.index(line), line)
            try:
                if line.split(';')[-1].strip('\n') == c and line.split(';')[2].lower() not in line_vars:
                    line_vars.append(line.split(';')[2].lower())
                if line.split(';')[0].lower().strip('\n') in countries_ru and line.split(';')[0].strip('\n').lower() in line_vars:
                    line_vars.remove(line.split(';')[0].strip('\n').lower())
                    line_vars.insert(0,line.split(';')[0].strip('\n').lower())
            except:
                try:
                    if line.split('\t')[-1].strip('\n') == c and line.split(';')[2].lower() not in line_vars:
                        line_vars.append(line.split(';')[2].lower())
                    if line.split('\t')[0].lower().strip('\n') in countries_ru and line.split(';')[0].strip('\n').lower() in line_vars:
                        line_vars.remove(line.split(';')[0].strip('\n').lower())
                        line_vars.insert(0,line.split(';')[0].strip('\n').lower())
                except:
                    continue

                #print(f.index(line), line)
                #break
        variants.append({c:line_vars})
    return variants, countries_ru

global variants
variants, countries_ru = urlCountry()
all_countries = []
for i in variants:
    all_countries += [word.lower() for word in list(i.values())[0]]
all_countries = list(set(all_countries))

def leave(req, res):
    res['response']["end_session"] = True
    res['response']['text'] = 'Всего доброго!'
    res['response']['buttons'] = []
    return

def greets(req, res):
    global link
    global buts
    link = ''
    firstgreets = ['Привет! Этот навык поможет \
           рассчитать стоимость страховки для путешественников, а также узнать\
           о других страховых продуктах Ингосстраха. Выберите вид страхования.\
           Чтобы посчитать стоимость туристической страховки, выберите "Путешествия"',
           'Здравствуйте! Я помогу рассчитать стоимость страховки для путешественников \
           и расскажу о видах страхования в Ингосстрахе. Что вас интересует?',
           'Добрый день. Здесь можно рассчитать стоимость туристической страховки \
           и узнать о других видах страхования в Ингосстрахе. Что нужно застраховать?']
    firstgreet = random.choice(firstgreets)
    nextgreets = ['Да-да, здесь все еще можно рассчитать \
           стоимость туристической страховки и узнать о продуктах Ингосстраха. \
           Какой вид страхования вас интересует?',
           'И снова здравствуйте! Выберите "Путешествия" для расчета стоимости \
           полиса путешественника. Выберите другие продукты, чтобы узнать о них больше.',
           'Не стесняйтесь! Что нужно застраховать? Выберите "Путешествия" для \
           расчета стоимости полиса путешественника. Выберите другие продукты, \
           чтобы узнать о них больше.']
    nextgreet = random.choice(nextgreets)
    buttons = [
            {"title": "Путешествия",
             "hide": True},
    {"title": "Автомобили",
     "hide": True},
     {"title": "Здоровье и жизнь",
      "hide": True},
      {"title": "Инвестиции и пенсия",
       "hide": True},
       {"title": "Имущество",
        "hide": True},
        {"title": "Выход",
        "hide": True}]
    res['response']['buttons'] = buttons
    if req['session']['new'] == True:
        res['response']['text'] = firstgreet
    elif req['session']['new'] == False:
        res['response']['text'] = nextgreet
    if req['request']['original_utterance'].lower() in ['закончить', 'выход', 'завершить','закончить.', 'выход.', 'завершить.']:
        leave(req,res)
    return greets

def products(req, res):
    prod = ''
    if re.match(r'авто|машин|каско|осаго', req['request']['original_utterance'].lower()): 
        res['response']['text'] = 'Воспользуйтесь программами страхования \
        транспортных средств и застрахуйте возможные риски, связанные с \
        эксплуатацией автомобиля.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/auto/","hide": True},
           {"title": "В начало","hide": True},{"title": "Выход","hide": True}]
        prod = 'auto'
    elif re.match(r'жизн|здоров|медиц|спор', req['request']['original_utterance'].lower()): 
        res['response']['text'] = 'Жизнь и здоровье - самые ценные ресурсы любого \
        человека. Мы предлагаем разные продукты в этой сфере: от страхования от \
        несчастного случая на соревнованиях до ДМС для получения качественной \
        медицинской помощи.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/health_life/","hide": True},
           {"title": "В начало","hide": True},{"title": "Выход","hide": True}]
        prod = 'life'
    elif re.match(r'инвест|пенси|пожил', req['request']['original_utterance'].lower()): 
        res['response']['text'] = 'Мы предлагаем не только программы пенсионного \
        страхования, но и различные инструменты для инвестирования.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/pension_investment/","hide": True},
           {"title": "В начало","hide": True},{"title": "Выход","hide": True}]
        prod = 'inv'
    elif re.match(r'имущ|недвиж|квартир|дом|дач', req['request']['original_utterance'].lower()): 
        res['response']['text'] = 'Страхование имущества — дома, квартиры или дачи — \
        это возможность защитить имущество и уберечь себя от непредвиденных финансовых затрат.'
        res['response']['buttons'] = [{"title": "Узнать больше.","url": "https://www.ingos.ru/property/","hide": True},
           {"title": "В начало","hide": True},{"title": "Выход","hide": True}]
        prod = 'prop'
    elif re.match(r'путешест|грани|рубеж|поех|поез', req['request']['original_utterance'].lower()): 
        vzr.country(req, res)
        #prod = 'travel'
        return
    elif re.match(r'заверш|законч|выход|выйти|выйди', req['request']['original_utterance'].lower()): 
        leave(req,res)
    elif re.match(r'нач|занов', req['request']['original_utterance'].lower()) or 'в начало' in req['request']['original_utterance'].lower(): 
        greets(req, res)
        return
    elif 'узнать больше' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Надеюсь, моя помощь оказалась полезной. Обязательно \
        ознакомьтесь с нашими предложениями по другим страховым продуктам.'
        res['response']['buttons'] = [{"title": "В начало","hide": True},{"title": "Выход","hide": True}]
    elif 'помощ' in req['request']['original_utterance'].lower() or 'помог' in req['request']['original_utterance'].lower() or 'что ты умеешь' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Я могу помочь вам рассчитать стоимость страховки \
        для путешествий, а также рассказать о других видах страхования в Ингосстрахе. \
        Чтобы рассчитать стоимость полиса для путешественника, выберите "Путешествия". \
        Для расчета нужно знать страну поездки, даты, количество и возраст путешественников. \
        Чтобы ознакомиться с другими продуктами, выберите их из списка ниже.'
        buttons = [
            {"title": "Путешествия",
             "hide": True},
            {"title": "Автомобили",
             "hide": True},
             {"title": "Здоровье и жизнь",
              "hide": True},
              {"title": "Инвестиции и пенсия",
               "hide": True},
               {"title": "Имущество",
                "hide": True},
                {"title": "Выход",
                "hide": True}]
        res['response']['buttons'] = buttons
    else:
        if req['session']['new'] == False:
            #if prod != 'travel':
            res['response']['text'] = 'Кажется, я вас не понимаю. Выберите "Путешествия" \
                для расчета стоимости туристической страховки, либо другой страховой продукт, \
                чтобы узнать о нем больше.'
            #if len(vzr.dates) == 1:
    return products

class vzr:
    asia = 0
    url = url = 'https://www.ingos.ru/travel/abroad/calc/?utm_source=alisa-yandex&utm_medium=organic&utm_campaign=vzr_alisa&country={}&datebegin={}&dateend={}&years={}'
    countries = []
    countries_rus = []
    dates = {}
    ages = ''
    def country(req, res):
        vzr.countries.clear()
        vzr.countries_rus.clear()
        global country_buttons
        country_buttons = [{"title": "Шенген", "hide": True},
           {"title": "Италия", "hide": True},
           {"title": "Испания", "hide": True},
           {"title": "В начало","hide": True},
           {"title": "Выход","hide": True}]
        res['response']['buttons'] = country_buttons
        res['response']['text'] = random.choice(['В каких странах вы собираетесь \
           пользоваться страховкой? Укажите первую страну посещения.',
           'Для каких стран вам нужна страховка? Назовите первую страну для посещения.'])
        return

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

    def checkFin(req, res):
        global check_buttons
        check_buttons = [{"title": "Ясно, указать даты", "hide": True},
           {"title": "Изменить список стран", "hide": True},
           {"title": "В начало", "hide": True},
           {"title": "Выход", "hide": True}]
        res['response']['buttons'] = check_buttons
        res['response']['text'] = 'Не забудьте! Для получения визы Финляндии \
        полис должен действовать на момент подачи заявления.  Установите датой \
        начала поездки дату подачи документов в посольство.'
        return

    def checkAsia(req, res):
        global check_buttons
        res['response']['buttons'] = check_buttons
        res['response']['text'] = 'Cтраховой полис для стран Юго-Восточной Азии \
        может быть оформлен не позднее, чем за 5 календарных дней до начала \
        запланированной поездки.'
        return
    
    def date_hints(delta):
        hints = []
        ru_months = ['декабря', 'января', 'февраля', 'марта', 'апреля', 'мая',
                     'июня','июля', 'августа', 'сентября', 'октября', 'ноября']
        hint1 = (datetime.today() + timedelta(days=delta)).strftime('%d.%m.%Y')
        if hint1[0] == '0':
            hint1 = hint1[1:]
        d = hint1.split('.')
        if d[1] == '12':
            d.remove(d[1])
            d.insert(1,ru_months[0])
        elif d[1] == '01' or d[1] == 1:
            d.remove(d[1])
            d.insert(1,ru_months[1])
        else:
            for m in ru_months:
                if d[1] == str(ru_months.index(m)):
                    d.remove(d[1])
                    d.insert(1, m)
        hint2 = ' '.join(d)
        if hint2[0] == '0':
            hint2 = hint2[1:]
        hints = [hint1,hint2]
        return hints
        
    def dateBegin(req, res):
        vzr.dates = {}
        global db_but
        hints = vzr.date_hints(7)
        db_but = [{"title": hints[0], "hide": True},
                  {"title": hints[1], "hide": True},
                  {"title": "В начало", "hide": True},
                  {"title": "Выход", "hide": True}]
        res['response']['buttons'] = db_but
        res['response']['text'] = random.choice(['Когда начинается ваше путешествие?',
           'С какой даты необходимо оформить полис?'])
        res['response']['tts'] = random.choice(['Когда начинается ваше путешествие? \
           Укажите дату в формате день, месяц, год.',
           'С какой даты необходимо оформить полис? Укажите дату в формате день, месяц, год.'])
        return

    def dateEnd(req, res, step):
        global de_but
        hints = vzr.date_hints(14)
        de_but = [{"title": hints[0], "hide": True},
                  {"title": hints[1], "hide": True},
                  {"title": "В начало", "hide": True},
                  {"title": "Выход", "hide": True}]
        res['response']['buttons'] = de_but
        if step == 1:
            res['response']['text'] = random.choice(['Когда заканчивается поездка?',
               'Когда полис должен закончить действие?'])
            res['response']['tts'] = random.choice(['Когда заканчивается поездка? \
               Укажите дату в формате день, месяц, год.',
               'Когда полис должен закончить действие?Укажите дату в формате день, месяц, год.'])
            return
        else:
            res['response']['text'] = 'Дата указана некорректно. Дата завершения \
            поездки не может быть раньше даты начала. Укажите точную дату окончания \
            поездки: день, месяц, год.'
            return
        if len(vzr.dates) == 1:
            if "YANDEX.DATETIME" in str(req['request']['nlu']['entities']):
                if 'year' not in str(req['request']['nlu']['entities']) or 'month' not in str(req['request']['nlu']['entities']) or 'day' not in str(req['request']['nlu']['entities']):
                    vzr.ages = ''
                    res['response']['text'] = 'Укажите, пожалуйста, точную дату \
                    окончания поездки: день, месяц, год.'
                    hints = vzr.date_hints(14)
                    de_but = [{"title": hints[0], "hide": True},
                      {"title": hints[1], "hide": True},
                      {"title": "В начало", "hide": True},
                      {"title": "Выход", "hide": True}]
                    res['response']['buttons'] = de_but
                    return
                else:
                    vzr.ages = ''
                    if 'YANDEX.NUMBER' in str(req['request']['nlu']['entities']) and 'YANDEX.GEO' not in str(req['request']['nlu']['entities']):
                        clear_date = str(req['request']['nlu']['entities'][1]['value']['day'])+'.'+str(req['request']['nlu']['entities'][1]['value']['month'])+'.'+str(req['request']['nlu']['entities'][1]['value']['year'])
                    if 'YANDEX.GEO' in str(req['request']['nlu']['entities']):
                        clear_date = str(req['request']['nlu']['entities'][2]['value']['day'])+'.'+str(req['request']['nlu']['entities'][2]['value']['month'])+'.'+str(req['request']['nlu']['entities'][2]['value']['year'])
                    else:
                        clear_date = str(req['request']['nlu']['entities'][0]['value']['day'])+'.'+str(req['request']['nlu']['entities'][0]['value']['month'])+'.'+str(req['request']['nlu']['entities'][0]['value']['year'])
                    vzr.parseDate(clear_date,req,res)
                    return


    def parseDate(date, req, res):
        global db_but
        global de_but
        def reverseDate(date):
            for c in date:
                if c in list(punctuation):
                    date = date.replace(c, ' ')
            fine_date = date.split()
            fine_date.reverse()
            return fine_date
        fine_date = reverseDate(date)
        res['response']['buttons'] = db_but
        def checkDate(fine_date):
            months = {'декабр':12,'январ':1,'феврал':2,'март':3,'апрел':4,'май':5,'мая':5,'июн':6,
                      'июл':7,'август':8,'сентябр':9,'октябр':10,'ноябр':11}
            for i in range(len(list(months.keys()))):
                if list(months.keys())[i] in str(fine_date[1]):
                    fine_date.remove(fine_date[1])
                    fine_date.insert(1,list(months.values())[i])
            return fine_date
        fine_date = checkDate(fine_date)
        if len(vzr.dates) == 0 and datetime(int(fine_date[0]),int(fine_date[1]),int(fine_date[2])) <= datetime.today():
            res['response']['text'] = 'Дата не может быть раньше завтрашнего дня.'
            res['response']['tts'] = 'Дата не может быть раньше завтрашнего дня. \
            Введите дату в формате день, месяц, год.'
            res['response']['buttons'] = db_but
            return
        elif len(vzr.dates) == 1 and datetime(int(fine_date[0]),int(fine_date[1]),int(fine_date[2])) <= datetime(int(vzr.dates['1st'].split('.')[2]),int(vzr.dates['1st'].split('.')[1]),int(vzr.dates['1st'].split('.')[0])):
            res['response']['text'] = 'Дата окончания действия полиса указана \
            некорректно. Введите дату завершения поездки.'
            res['response']['buttons'] = de_but
            return
        elif len(vzr.dates) == 0 and datetime(int(fine_date[0]),int(fine_date[1]),int(fine_date[2])) > datetime.today():
            if vzr.asia == 1:
                if datetime(int(fine_date[0]),int(fine_date[1]),int(fine_date[2])) > datetime.today() + timedelta(days = 5):
                    vzr.dates['1st']=str(fine_date[2])+'.'+str(fine_date[1])+'.'+str(fine_date[0])
                else:
                    res['response']['text'] = 'Для стран Юго-Восточной Азии \
                    ближайшая дата начала действия полиса'+str((datetime.today()+timedelta(days = 5)).strftime("%d-%m-%Y"))+'. Выберите эту дату или ведите другую.'
                    res['response']['buttons'] = db_but.insert(0,str((datetime.today()+timedelta(days = 5)).strftime("%d-%m-%Y")).replace('-','.'))
                    return
                    vzr.dates['1st']=str((datetime.today()+timedelta(days = 5)).strftime("%d-%m-%Y")).replace('-','.')
            else:
                vzr.dates['1st']=str(fine_date[2])+'.'+str(fine_date[1])+'.'+str(fine_date[0])
        elif len(vzr.dates) == 1 and datetime(int(fine_date[0]),int(fine_date[1]),int(fine_date[2])) > datetime(int(vzr.dates['1st'].split('.')[2]),int(vzr.dates['1st'].split('.')[1]),int(vzr.dates['1st'].split('.')[0])):
            vzr.dates['2nd']=str(fine_date[2])+'.'+str(fine_date[1])+'.'+str(fine_date[0])
        return vzr.dates
    
    

vzr.ages = ''
vzr.countries.clear()
vzr.countries_rus.clear()
vzr.dates = {}
vzr.url = 'https://www.ingos.ru/travel/abroad/calc/?utm_source=alisa-yandex&utm_medium=organic&utm_campaign=vzr_alisa&country={}&datebegin={}&dateend={}&years={}'
# Функция для непосредственной обработки диалога.
step = 1
def handle_dialog(req, res):
    global country_buttons
    global link
    global profile
    global step
    profile = ''
    greets(req, res)
    products(req, res)
    if re.match(r'путешест|грани|рубеж|поех|поез', req['request']['original_utterance'].lower()): 
        profile = 'travel'
        vzr.country(req, res)
        return
    if re.match(r'нач|занов', req['request']['original_utterance'].lower()):
        greets(req, res)
        return
    if req['request']['original_utterance'].lower() in all_countries:
        while req['request']['original_utterance'].lower() in all_countries and req['request']['original_utterance'].lower() != '':
            for v in variants:
                if req['request']['original_utterance'].lower() in list(v.values())[0]:
                    chozen_country = list(v.values())[0][0]
                    vzr.countries.append(list(v.keys())[0])
                    vzr.countries_rus.append(chozen_country)
                    vzr.nextCountry(req, res)
                    return
    elif req['request']['original_utterance'].lower() not in all_countries and profile == 'travel': 
        if len(vzr.countries_rus) == 0:
            res['response']['text'] = 'Боюсь, я вас не понимаю. Укажите первую страну вашей поездки.'
            country_buttons = [{"title": "Шенген", "hide": True},
           {"title": "Италия", "hide": True},
           {"title": "Испания", "hide": True},
           {"title": "В начало","hide": True},
           {"title": "Выход","hide": True}]
            res['response']['buttons'] = country_buttons
            return
        elif len(vzr.countries_rus) > 0:
            res['response']['text'] = 'Не понимаю. Вы выбрали: {}. Укажите \
            следующую страну вашей поездки или перейдите на следующий шаг.'.format(str(list(set(vzr.countries_rus))).strip("\[\]").replace("'",'').upper())
            country_buttons = [{"title": "Следующий шаг", "hide": True},
                               {"title": "Шенген", "hide": True},
                               {"title": "Италия", "hide": True},
                               {"title": "Испания", "hide": True},
                               {"title": "В начало","hide": True},
                               {"title": "Выход","hide": True}]
            res['response']['buttons'] = country_buttons#'''
            
    if  re.match(r'.*мен.* стран',req['request']['original_utterance'].lower()):
        vzr.country(req, res)
        return
    if 'следующий шаг' in req['request']['original_utterance'].lower() or 'закончить список' in req['request']['original_utterance'].lower() or 'дальше' in req['request']['original_utterance'].lower():
        if 'finliandiia' in vzr.countries:
            vzr.checkFin(req, res)
            return
        elif 'aziya' in vzr.countries:
            vzr.asia = 1
            vzr.checkAsia(req, res)
            return
        vzr.dateBegin(req, res)
        step = 1
        return
    elif 'ясно' in req['request']['original_utterance'].lower() or re.match(r'.*мен.* дат',req['request']['original_utterance'].lower()) or "поня" in req['request']['original_utterance'].lower():
        profile = ''
        vzr.ages = ''
        vzr.dateBegin(req, res)
        step = 1
        return
    elif "получить" in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Надеюсь, моя помощь оказалась полезной. Обязательно ознакомьтесь с нашими предложениями по другим страховым продуктам - вернитесь в начало диалога.'
        res['response']['buttons'] = [{"title": "В начало","hide": True},{"title": "Выход","hide": True}]
        vzr.ages = ''
        vzr.countries.clear()
        vzr.countries_rus.clear()
        vzr.dates = {}
        link = ''
    elif "спасиб" in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Всегда рады помочь! Не забудьте узнать о наших остальных продуктах - вернитесь в начало диалога.'
        res['response']['buttons'] = [{"title": "В начало","hide": True},{"title": "Выход","hide": True}]
    elif "YANDEX.DATETIME" in str(req['request']['nlu']['entities']):
        if 'year' not in str(req['request']['nlu']['entities']) or 'month' not in str(req['request']['nlu']['entities']) or 'day' not in str(req['request']['nlu']['entities']):
            res['response']['text'] = 'Пожалуйста, укажите точную дату начала поездки: день, месяц, год.'
            hints = vzr.date_hints(7)
            db_but = [{"title": hints[0], "hide": True},
                  {"title": hints[1], "hide": True},
                  {"title": "В начало", "hide": True},
                  {"title": "Выход", "hide": True}]
            res['response']['buttons'] = db_but
        else:
            if 'YANDEX.NUMBER' in str(req['request']['nlu']['entities']) and 'YANDEX.GEO' not in str(req['request']['nlu']['entities']):
                clear_date = str(req['request']['nlu']['entities'][1]['value']['day'])+'.'+str(req['request']['nlu']['entities'][1]['value']['month'])+'.'+str(req['request']['nlu']['entities'][1]['value']['year'])
            elif 'YANDEX.GEO' in str(req['request']['nlu']['entities']):
                clear_date = str(req['request']['nlu']['entities'][2]['value']['day'])+'.'+str(req['request']['nlu']['entities'][2]['value']['month'])+'.'+str(req['request']['nlu']['entities'][2]['value']['year'])
            else:
                clear_date = str(req['request']['nlu']['entities'][0]['value']['day'])+'.'+str(req['request']['nlu']['entities'][0]['value']['month'])+'.'+str(req['request']['nlu']['entities'][0]['value']['year'])
            vzr.parseDate(clear_date,req,res)
        
        if len(vzr.dates) == 1:
            vzr.ages = ''
            while len(vzr.dates) != 2:
                vzr.ages = ''
                vzr.dateEnd(req, res, step)
                step += 1
                vzr.ages = ''
                return step

    if (len(vzr.dates) == 2 and len(vzr.ages) == 0) or "менить возраст" in req['request']['original_utterance'].lower() or "менять возраст" in req['request']['original_utterance'].lower():
        link = ''
        vzr.ages = ''
        res['response']['text'] = 'Сколько полных лет каждому путешественнику на текущую дату? Например так: 30, 30, 32'
        buts = [{"title": "В начало", "hide": True},
                {"title": "Выход", "hide": True}]
        res['response']['buttons'] = buts
        vzr.ages = req['request']['original_utterance']
        return vzr.ages
    elif len(vzr.dates) == 2 and len(vzr.countries) != 0 and len(vzr.ages) != 0:
        fine_ages = []
        if len(fine_ages) == 0:
            o = req['request']['nlu']['entities']
            if len(o) != 0 and not re.match(r'заверш|законч|выход|выйти|выйди|нач|занов|помог|помощ|что ты умеешь', req['request']['original_utterance'].lower()):#req['request']['original_utterance'].lower() not in ['закончить', 'выход', 'завершить','закончить.', 'выход.', 'завершить.'] and req['request']['original_utterance'].lower() not in ['в начало', 'заново', 'начать сначала','в начало.', 'заново.', 'начать сначала.'] and 'помощь' not in req['request']['original_utterance'].lower() and 'что ты умеешь' not in req['request']['original_utterance'].lower() and 'помоги' not in req['request']['original_utterance'].lower():
                for i in o:
                    try:
                        if int(i['value']):
                            fine_ages.append(str(i['value']))
                    except:
                        continue
                res['response']['text'] = 'Укажите возраст каждого из путешественников на текущую дату. Например так: 30, 30, 32'
                res['response']['buttons'] = [{"title": "В начало", "hide": True},
                {"title": "Выход", "hide": True}]
            elif re.match(r'заверш|законч|выход|выйти|выйди', req['request']['original_utterance'].lower()):
                leave(req,res)
            elif re.match(r'нач|занов', req['request']['original_utterance'].lower()): 
                greets(req, res)
            elif 'помощ' in req['request']['original_utterance'].lower() or 'помог' in req['request']['original_utterance'].lower() or 'что ты умеешь' in req['request']['original_utterance'].lower():
                res['response']['text'] = 'Я могу помочь вам рассчитать стоимость страховки \
        для путешествий, а также рассказать о других видах страхования в Ингосстрахе. \
        Чтобы рассчитать стоимость полиса для путешественника, выберите "Путешествия". \
        Для расчета нужно знать страны поездки, даты, количество и возраст путешественников. \
        Чтобы ознакомиться с другими продуктами, выберите их из списка ниже.'
                buttons = [
                    {"title": "Путешествия",
                     "hide": True},
                    {"title": "Автомобили",
                     "hide": True},
                     {"title": "Здоровье и жизнь",
                      "hide": True},
                      {"title": "Инвестиции и пенсия",
                       "hide": True},
                       {"title": "Имущество",
                        "hide": True},
                        {"title": "Выход",
                        "hide": True}]
                res['response']['buttons'] = buttons
        if len(fine_ages) > 0:
            vzr.ages = ','.join(fine_ages)
            link = vzr.url.format(str(vzr.countries[0]).strip("\[\]").replace("'",''),vzr.dates['1st'],vzr.dates['2nd'],vzr.ages.strip('.')).strip("\[\]").replace("'",'').replace(' ','')
            #ВСЕ СТРАНЫ: link = vzr.url.format(str(vzr.countries).strip("\[\]").replace("'",''),vzr.dates['1st'],vzr.dates['2nd'],vzr.ages.strip('.')).strip("\[\]").replace("'",'').replace(' ','')
        
    if len(link) > 0:
        res['response']['text'] = '''
        Вы выбрали страны: {}. 
        Дата начала действия полиса - {}, 
        дата окончания действия полиса - {}. 
        Возраст путешественников: {}'''.format(str(list(set(vzr.countries_rus))).strip("\[\]").replace("'",'').upper(),str(vzr.dates['1st']),str(vzr.dates['2nd']),str(vzr.ages)).strip("\['\]").replace("'",'')
        res['response']['tts'] = 'Ваш полис почти готов! Перед покупкой обязательно еще раз проверьте все данные.'
        res['response']['buttons'] = [{"title": "Получить полис","url": link,"hide": True}, 
                {"title": "Изменить страну", "hide": True},
                {"title": "Изменить даты", "hide": True},
                {"title": "Изменить возраст путешественников", "hide": True},
                {"title": "В начало", "hide": True},
                {"title": "Выход", "hide": True}]
