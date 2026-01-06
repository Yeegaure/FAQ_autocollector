import pandas as pd
from typing import List

import spacy as sp
from spacy.matcher import Matcher

import re

nlp = spacy.load("ru_core_news_sm")

remove_start = {"а", "кстати", "то"}
negative_ptr = {"это", "там", "ты", "тут", "вот"}
negative_connectors = {"или", "и", "вы", "ну", "так", "да", "разве", "о"}
positive_words = {"подскажите", "подскажи", "ребят", "ребята", "коллеги", "друзья",
                  "кто-нибудь", "всем", "кто-то", "привет", "здравствуйте", "доброго"}
positive_combinations = { "если", "может", "я", "не", "можно", "в", "никто", "можете", "у" }
uncertain = {"на", "с", "интересно", "для", "мне"}
question_words = {"как", "что", "сколько", "где", "какой", "кто", "когда",
                  "почему", "чем", "чего", "куда", "который", "кому", "зачем",
                  "откуда", "чей", "чья", "каков", "отчего"}

pattern_esli_to = [{'LOWER': 'если'},
                        {'OP': '*'},
                        {'LOWER': 'то'}]

pattern_ya_verno = [{'LOWER': 'я'},
                        {'OP': '*'},
                        {'LOWER': 'верно'}]

pattern_ya_ponyal = [{'LOWER': 'я'},
                     {'OP': '*'},
                     {'LOWER': 'правильно'},
                     {'OP': '*'},
                     {'LEMMA': {'IN': ['понял', 'понимаю']}}]

pattern_v_etc = [{'LOWER': 'в'},
                 {'LOWER': {'IN': list(question_words)}}]

pattern_v_suffix = [{'LOWER': 'в'},
                    {'TEXT': {'REGEX': r'.*(их|ой|ом)$'}}]

pattern_nikto_ne = [{'LOWER': 'никто'},
                    {'OP': '*'},
                    {'LOWER': 'не'}]
pattern_mojet_kto_nibud = [{'LOWER': 'может'},
                           {'OP': '*'},
                           {'LOWER': {'IN': ['кто', 'кто-нибудь']}}]

pattern_u_kogo_nibud = [{'LOWER': 'у'},
                        {'OP': '*'},
                        {'LOWER': 'кого-нибудь'}]

pattern_mojno_li_uznat = [{'LOWER': 'можно'},
                        {'OP': '*'},
                        {'LOWER': {'IN': ['ли', 'узнать']}}]

pattern_ne_znaete_podskajite = [{'LOWER': 'не'},
                        {'OP': '*'},
                        {'LOWER': {'IN': ['знаете', 'подскажите']}}]

pattern_mojete = [{'LOWER': 'можете'}]


matcher = Matcher(nlp.vocab)
matcher.add('YA_PRAVILNO_PONYAL', [pattern_esli_to])
matcher.add('V_QUESTION_WORD', [pattern_ya_verno])
matcher.add('YA_PRAVILNO_PONYAL', [pattern_ya_ponyal])
matcher.add('V_QUESTION_WORD', [pattern_v_etc])
matcher.add('V_SUFFIX', [pattern_v_suffix])
matcher.add('NIKTO_NE', [pattern_nikto_ne])
matcher.add('MOJET_KTO_NIBUD', [pattern_mojet_kto_nibud])
matcher.add('U_KOGO_NIBUD', [pattern_u_kogo_nibud])
matcher.add('NIKTO_NE', [pattern_mojno_li_uznat])
matcher.add('MOJET_KTO_NIBUD', [pattern_ne_znaete_podskajite])
matcher.add('U_KOGO_NIBUD', [pattern_mojete])


def tokenize_text(text: str) -> List[str]:
    '''lowercase, tokenize and remove punctuation'''
    text = text.lower().strip()
    doc = nlp(text)
    tokens = [t.text for t in doc if not t.is_punct]
    return tokens, doc

def classify_questions(text: str) -> int:
    '''questions classification based on euristics'''

    tokens, doc = tokenize_text(text)

    matchers = matcher(doc)

    if not tokens:
        return 2

    while tokens and tokens[0] in remove_start:
        tokens.pop(0)

    if not tokens:
        return 2

    first_token = tokens[0]

    # 0 not informative
    if first_token in negative_ptr or first_token in negative_connectors: return 0

    if matchers: return 0

    # 1 informative + добавить обращение TODO
    if first_token in positive_words: return 1

    if first_token in question_words: return 1
    if any(q in tokens for q in question_words): return 1
    if first_token == "а" and len(tokens) > 1 and tokens[1] in question_words: return 1

    # 2 unsure
    if first_token in uncertain: return 2

    return 2


def classify_df(df: pd.DataFrame) -> pd.DataFrame:
    df["prediction"] = df["premise"].apply(classify_questions)
    return df

def classify_list(messages: list[str]) -> pd.DataFrame:
    return pd.DataFrame({'message' : messages,
                         'classification' : [classify_questions(msg) for msg in messages]})