
# -*- coding: utf-8 -*-

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import pymorphy2
from collections import Counter

stop_words = stopwords.words('russian')
stop_words.extend(["например", "также", "нибудь", "который", "свой", "обычно", "некоторый", "кому"])
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
morph = pymorphy2.MorphAnalyzer()

def dict_to_wordlist(text, remove_stopwords=True):
    words = []
    gram_info = []
    text = re.sub("[^а-яА-Я]"," ", text)
    all_words = text.lower().split()
    for word in all_words:
        p = morph.parse(word)[0]
        if word not in stop_words and  p.normal_form not in stop_words:
            words.append({word:p.normal_form})
            gram_info.append({p.normal_form:str(p.tag)})
    return(words,gram_info)
    
def def_to_sentences(text,tokenizer, remove_stopwords=True):
    raw_sentences = tokenizer.tokenize(text.strip())
    sentences = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(dict_to_wordlist(raw_sentence,remove_stopwords))
    return sentences
        
i = 0
_dict = pd.read_csv( "output1.csv", header=0,delimiter=";")
print('Read dict')

defs = []
definitions = []
normalized_data= []
for art in _dict["DEF"]:
    defs.append([str(art)])
for _def in defs:
    _def.insert(0,_dict["VOCAB"][i])
    i += 1
    definitions.append(str(_def).strip('[]'))

for definition in definitions:
    definition = definition.replace('.',';')
    normalized_data += def_to_sentences(definition, tokenizer)
    
print('Data normalized')

nouns = []
adjs = []
verbs = []
advs = []
for sentence in normalized_data:
    for word in sentence[-1]:
        n = re.search('NOUN',list(word.values())[0])
        aj = re.search('ADJF',list(word.values())[0])
        v = re.search('VERB',list(word.values())[0])
        av = re.search('ADVB',list(word.values())[0])
        if n != None:
            nouns.append(list(word.keys())[0])
        elif aj != None:
            adjs.append(list(word.keys())[0])
        elif v != None:
            verbs.append(list(word.keys())[0])
        elif av != None:
            advs.append(list(word.keys())[0])
            
print('PoS lists created')
        
'''c = Counter(nouns).most_common()
for element in c[:500]:
    if [element[0]] not in stop_words: 
        stop_words.extend([element[0]])'''
        
dice_dict = []
all_words = ['аббат']#nouns + adjs + verbs + adjs
#отношение количества совпадающих слов в двух дефинициях к сумме слов в его толковании
#def_overlap/words_sum

with open('RESULT.txt','w',encoding = 'utf-8') as f:
    for defin in normalized_data:
        data1 = defin[0]
        words_sum = len(data1)
        for defin2 in normalized_data:
            if defin2 != defin:
                data2 = defin2[0]
            def_overlap = {}
            sum_i = 0
            i = 0
            for word in data1:
                if word in data2:
                    i += 1
                    #print(word, data1, i)
            sum_i += i
            if sum_i != 0:
                #def_overlap[list(word.values())[0]] = sum_i
                dice = sum_i / words_sum
                if dice >= 0.5: 
                    print(data1[0],data2[0],dice)
                f.write(str(data1[0])+str(data2[0])+str(dice))
            
