import spacy
import pandas as pd

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


def qestions_classifier(text: str) -> int:
    nlp = spacy.load("ru_core_news_sm")
    # tokenize: remove punctuation and make  lower
    doc = nlp(text)
    text = " ".join([t.text for t in doc if not t.is_punct])
    doc = nlp(text.lower().strip())


    tokens = [t.text for t in doc if not t.is_space]
    if not tokens:
        return 2

    while tokens and tokens[0] in remove_start:
        tokens.pop(0)

    if not tokens:
        return 2

    first, second = tokens[0], tokens[1]

    # 0 not informative
    if first in negative_ptr: return 0
    if first in negative_connectors: return 0
    if "если" in tokens: return 0

    if ("если" in tokens and "то" in tokens) and (tokens.index("если") < tokens.index("то")): return 0
    if "я" in tokens:
        if "правильно" in tokens:
            if tokens.index("правильно") > tokens.index("я"):
                if "понял" in tokens:
                    if tokens.index("понял") > tokens.index("правильно"): return 0
                if "понимаю" in tokens:
                    if tokens.index("понимаю") > tokens.index("правильно"): return 0

    if "верно" in tokens and tokens.index("верно") > tokens.index("я"): return 0

    # в + (вопрос)
    if "в" in tokens:
        if tokens.index("в") + 1 < len(tokens):
            next = tokens[tokens.index("в") + 1]
            if next in question_words: return 0
            if next.endswith(("их", "ой", "ом")): return 0
    if "никто" in tokens and "не" in tokens and (tokens.index("никто") < tokens.index("не")): return 0
    if "может" in tokens and ("кто" in tokens or "кто-нибудь" in tokens): return 0
    if "у" in tokens and "кого-нибудь" in tokens: return 0

    # 1 informative + добавить обращение TODO
    if first in positive_words: return 1
    #if "подскажите" in tokens or "подскажи" in tokens: return 1
    if "можно" in tokens and ("ли" in tokens or "узнать" in tokens): return 1
    if "не" in tokens and ("знаете" in tokens or "подскажите" in tokens): return 1
    if "можете" in tokens: return 1

    # semantic patterns do we need '?'      ??????
    if first in question_words: return 1
    if any(q in tokens for q in question_words): return 1
    if first == "а" and len(tokens) > 1 and tokens[1] in question_words: return 1

    # 2 unsure
    if first in uncertain: return 2

    return 2


def df_classifier(df: pd.DataFrame) -> pd.DataFrame:
    df["prediction"] = df["premise"].apply(qestions_classifier)
    return df

def list_classifier(messages: list[str]) -> pd.DataFrame:
    return pd.DataFrame({'message' : messages,
                         'classification' : [qestions_classifier(msg) for msg in messages]})