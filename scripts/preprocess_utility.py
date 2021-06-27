import newspaper
import nltk
import re
import pandas as pd

from collections import Counter
from newspaper import Article, Source
from string import printable
from lxml import etree
from lxml.etree import tostring
from unidecode import unidecode

UPPERCASE_LETTERS = [chr(i) for i in range(65, 91)]
LOWERCASE_LETTERS = [chr(i) for i in range(97, 123)]
LETTERS = UPPERCASE_LETTERS + LOWERCASE_LETTERS
STOP_WORDS = Counter(nltk.corpus.stopwords.words('english'))


def lemmatization(sent):
    """Lemmatize sentence, remove stop words and non-english words
    Args:
        sent (sent): sentence to modify
    Returns:
        string: modified sentence
    """
    lemmatizer = nltk.stem.WordNetLemmatizer()
    new_sent = ""
    sent = sent.split(" ")
    for i in range(len(sent)):
        word = sent[i]
        cnt = word.count("|")
        if cnt > 1:
            continue
        elif cnt == 1:
            word = word.split("|")[1]
        filtered_word = ''.join(filter(lambda x: x in printable, word))
        # eliminate stop words and non-english words
        if 0 < len(word) == len(filtered_word) and word not in STOP_WORDS:
            punctuation = ""

            '''if the word ends in a punctuation mark,
            don't lemmatize the punctuation mark'''
            if word[-1] not in LETTERS:
                punctuation = word[-1]
                word = word[:-1]
            word = lemmatizer.lemmatize(word)
            new_sent += word + punctuation + " "

    return new_sent


def split_by_sentence_boundary(text, split_length=256, split_overlap=0):
    sentences = nltk.tokenize.sent_tokenize(text)
    word_count = 0
    list_splits = []
    current_slice = []
    for sen in sentences:
        current_word_count = len(sen.split(" "))
        if current_word_count > split_length:
            print(f"A sentence found with word count higher than the split length.")
        if word_count + current_word_count > split_length:
            list_splits.append(current_slice)
            if split_overlap:
                overlap = []
                w_count = 0
                for s in current_slice[::-1]:
                    sen_len = len(s.split(" "))
                    if w_count < split_overlap:
                        overlap.append(s)
                        w_count += sen_len
                    else:
                        break
                current_slice = list(reversed(overlap))
                word_count = w_count
            else:
                current_slice = []
                word_count = 0
        current_slice.append(sen)
        word_count += len(sen.split(" "))
    if current_slice:
        list_splits.append(current_slice)

    text_splits = []
    for sl in list_splits:
        txt = ' '.join(sl)
        if len(txt) > 0:
            text_splits.append(txt)

    return text_splits


def process_documents(document_dictionaries):
    for doc_dict in document_dictionaries:
        doc_dict["text"] = doc_dict["text"].replace(".\n", ". ")
        doc_dict["text"] = doc_dict["text"].replace("\n", " ")
        # Remove accented characters from text, e.g. café
        doc_dict["text"] = unidecode(doc_dict["text"])
        text_sents = nltk.tokenize.sent_tokenize(doc_dict["text"])
        new_sents = []
        for sent in text_sents:
            # new_sents.append(lemmatization(sent))
            new_sents.append(sent)
        doc_dict["text"] = "".join(new_sents)

    return document_dictionaries
