import sklearn
import math
import json
import numpy
import functools
import nltk
import re
import sys
import numpy as np
import spacy as sp
import pandas as pd

from spacy import displacy
from statistics import mean
from collections import Counter
from spacy.lemmatizer import Lemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.chunk import conlltags2tree, tree2conlltags
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity, pairwise_kernels
from sklearn.metrics import pairwise_distances

from django.core.management.base import BaseCommand

nlp = sp.load('en_core_web_sm')
lemmatizer = nlp.Defaults.create_lemmatizer()

stemmer = SnowballStemmer(language='english')


def find_candidate_sentences(question, sentences):
    '''
        Function that finds sentence answer candidates for a given question
    '''
    # frequency
    vectorizer = CountVectorizer(min_df=1)
    X = vectorizer.fit_transform(sentences)
    freq_term_corpus = X.toarray()
    freq_term_question = vectorizer.transform(question).toarray()
    
    # compute tf idf vectors
    transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_corpus = transformer.fit_transform(freq_term_corpus)
    tfidf_question = transformer.fit_transform(freq_term_question)

    # get cosine similarity
    list_cosine =[]
    for tc in tfidf_corpus:
        temp = cosine_similarity(tc, tfidf_question)
        list_cosine.append(temp[0,0])

    # get most similar sentence
    if max(list_cosine) != 0.0:
        index_max = list_cosine.index(max(list_cosine))
        sentence = sentences[index_max]
    else:
        sentence = None
    
    return sentence


def get_POS_tagging(sentence):
    '''
        Function that gets POS tagging for input sentence.
    '''
    sentence_tokens = nltk.word_tokenize(sentence)
    sentence_tagged = nltk.pos_tag(sentence_tokens)

    return(sentence_tokens, sentence_tagged)


def peform_named_entity_recognition(sentence):
    '''
        Function that performs NER on input sentence.
    '''
    document = nlp(sentence)
    return [(X, X.ent_iob_, X.ent_type_) for X in document]


def index(list, item):
    '''
        Helper function that searches for first index of an item inside a list.
    '''
    try:
        index = list.index(item)
    except ValueError:
        index = math.inf
    return index


def find_answer_type(sentence_candidate, question):
    sentence_tokens, _ = get_POS_tagging(sentence_candidate)
    sentence_candidate_named_entities = peform_named_entity_recognition(sentence_candidate)
    question_tokens, question_tags = get_POS_tagging(question)
    question_named_entities = peform_named_entity_recognition(question)

    question_words = ['who', 'what', 'how', 'when', 'where']
    question_type_index = min([index([token.lower() for token in question_tokens], question_word) for question_word in question_words])
    
    if question_type_index == math.inf:
        return None

    question_type = question_tags[question_type_index]
    question_type_next_word = question_tags[question_type_index + 1] if question_type_index + 1 < len(question_tokens) else None

    if question_type[0].lower() == 'who' and question_type_next_word and question_type_next_word[0].lower() == 'is':
        if  [item for item in question_named_entities if 'PERSON' in item[2]] != []:
            query = [str(item[0]) for item in question_named_entities if 'PERSON' in item[2]]
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'ORG'
            else:
                question_looking_for = None
        elif [item for item in question_named_entities if 'ORG' in item[2]] != []:
            query = [str(item[0]) for item in question_named_entities if 'ORG' in item[2]]
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'PERSON'
            else:
                question_looking_for = None           
        else:
            question_looking_for = None

    elif question_type[0].lower() == 'what' and question_type_next_word and question_type_next_word[0].lower() == 'time':
        query = [item[0] for item in question_tags if 'NN' in item]
        if query != []:
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'TIME'
                # print(question_looking_for)
            else:
                question_looking_for = None
        else:
            question_looking_for = None
            

    elif question_type[0].lower() == 'how' and question_type_next_word and question_type_next_word[0].lower() == 'much':
        query = [item for item in question_tags if 'NN' in item]
        if [query2 for query2 in query if 'money' in query2] != []:
            question_looking_for = 'MONEY'
            # print(question_looking_for)
        else:
            question_looking_for = None
            # print(question_looking_for)

    elif question_type[0].lower() == 'how' and question_type_next_word and question_type_next_word[0].lower() == 'many':
        query = [item[0] for item in question_tags if 'NNS' in item]
        if query != []:
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'QUANTITY'
                # print(question_looking_for)
            else:
                question_looking_for = None
        else:
            question_looking_for = None

    elif question_type[0].lower() == 'how' and question_type_next_word and question_type_next_word[0].lower() == 'big':
        query = [item[0] for item in question_tags if 'NN' in item]
        if query != []:
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'QUANTITY'
                # print(question_looking_for)
            else:
                question_looking_for = None
        else:
            question_looking_for = None

    elif question_type[0].lower() == 'how' and question_type_next_word and question_type_next_word[0].lower() == 'tall':
        query = [item[0] for item in question_tags if 'NNS' in item]
        if query != []:
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'QUANTITY'
                # print(question_looking_for)
            else:
                question_looking_for = None
        else:
            question_looking_for = None

    elif question_type[0].lower() == 'when':
        query = [item[0] for item in question_tags if 'NN' in item]
        if query != []:
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'DATE'
                # print(question_looking_for)
            else:
                question_looking_for = None
        else:
            question_looking_for = None

    elif question_type[0].lower() == 'where':
        query = [item[0] for item in question_tags if 'NN' in item]
        if query != []:
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'LOCATION'
                # print(question_looking_for)
            else:
                question_looking_for = None
        else:
            question_looking_for = None

    elif question_type[0].lower() == 'what':
        query = [item[0] for item in question_tags if 'NNP' in item]
        if query != []:
            if [check for check in query if check in sentence_tokens] != []:
                question_looking_for = 'DESCRIPTION'
                # print(question_looking_for)
            else:
                question_looking_for = None
        else:
            question_looking_for = None
    else:
        question_looking_for = None

    return question_looking_for        


def get_answer(question, sentence_candidate, answer_type):
    sentence_tokens, sentence_tags = get_POS_tagging(sentence_candidate)
    sentence_candidate_named_entities = peform_named_entity_recognition(sentence_candidate)
    _, question_tags = get_POS_tagging(question)
    
    if answer_type in ['ORG', 'PERSON', 'DATE', 'MONEY']:
        answer_words = [item[0] for item in sentence_candidate_named_entities if answer_type in item[2] ]
    elif answer_type ==  'TIME':
        pattern = r"\d{2}:\d{2}\s[A-Z]{4}"
        answer_words = re.findall(pattern, sentence_candidate)
    elif answer_type ==  'QUANTITY':
        query = [item for item in question_tags if 'NNS' in item[1]]
        answer_words = []
        if query != []:
            sentence_tags_query = [item for item in sentence_tags if 'NNS' in item[1]]
            matches = list(set(query).intersection(sentence_tags_query))
            if not matches:
                return []

            index_query = sentence_tags.index(matches[0])
            temp = []
            temp.append(sentence_tags[index_query-1])
            temp.append(sentence_tags[index_query-2])
            answer_words = [item[0] for item in temp if 'CD' in item[1]]
            if len(answer_words) < 1:
                answer_words = [item[0] for item in sentence_candidate_named_entities if 'QUANTITY' in item[2]]
    elif answer_type ==  'LOCATION':
        answer_words = [item[0] for item in sentence_candidate_named_entities if 'GPE' in item[2] ]
    elif answer_type ==  'DESCRIPTION':
        return sentence_candidate
    
    return functools.reduce(lambda el, other: el + str(other) + ' ', answer_words, '')


def question_answer(user_question, sentences):
    sentence_candidate = find_candidate_sentences([user_question], sentences)
    if not sentence_candidate:
        no_answer()
        return None

    answer_type = find_answer_type(sentence_candidate, user_question)
    if not answer_type:
        return sentence_candidate

    answer = get_answer(user_question, sentence_candidate, answer_type)
    if len(answer) <=1:
        return sentence_candidate

    return answer


def json_to_dataframe(file):
    f = open ( file , "r") 
    data = json.loads(f.read())               #loading the json file.
    iid = []                                  
    tit = []                                  #Creating empty lists to store values.
    con = []
    Que = []
    Ans_st = []
    Txt = []
    
    for i in range(len(data['data'])):       #Root tag of the json file contains 'title' tag & 'paragraphs' list.
        title = data['data'][i]['title']
        for p in range(len(data['data'][i]['paragraphs'])):  # 'paragraphs' list contains 'context' tag & 'qas' list.
            context = data['data'][i]['paragraphs'][p]['context']
            for q in range(len(data['data'][i]['paragraphs'][p]['qas'])):  # 'qas' list contains 'question', 'Id' tag & 'answers' list.
                question = data['data'][i]['paragraphs'][p]['qas'][q]['question']
                Id = data['data'][i]['paragraphs'][p]['qas'][q]['id']
                for a in range(len(data['data'][i]['paragraphs'][p]['qas'][q]['answers'])): # 'answers' list contains 'ans_start', 'text' tags. 
                    ans_start = data['data'][i]['paragraphs'][p]['qas'][q]['answers'][a]['answer_start']
                    text = data['data'][i]['paragraphs'][p]['qas'][q]['answers'][a]['text']
                    
                    tit.append(title)
                    con.append(context)
                    Que.append(question)                    # Appending values to lists
                    iid.append(Id)
                    Ans_st.append(ans_start)
                    Txt.append(text)

    new_df = pd.DataFrame(columns=['Id','title','context','question','ans_start','text']) # Creating empty DataFrame.
    new_df.Id = iid
    new_df.title = tit           #intializing list values to the DataFrame.
    new_df.context = con
    new_df.question = Que
    new_df.ans_start = Ans_st
    new_df.text = Txt

    final_df = new_df.drop_duplicates(keep='first')  # Dropping duplicate rows from the create Dataframe.
    return final_df

def compute_f1(answer_ground_truth, answer_prediction):
    ground_truth_tokens = nltk.word_tokenize(answer_ground_truth)
    prediction_tokens = nltk.word_tokenize(answer_prediction)

    common = Counter(ground_truth_tokens) & Counter(prediction_tokens)
    num_same = sum(common.values())

    if len(ground_truth_tokens) == 0 or len(prediction_tokens) == 0:
        return int(ground_truth_tokens == prediction_tokens)
    if num_same == 0:
        return 0
    
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)

    f1 = (2 * precision * recall) / (precision + recall)
    return f1

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # eval_file_path = '/app/static/nq/nq_dev_subset_v2.json'
        eval_file_path = '/app/static/output-test.squad.json'

        df = json_to_dataframe(eval_file_path)
        f1_values = []
        for index, row in df.iterrows():
            context_sentences = nltk.sent_tokenize(row['context'])
            predicted_answer = question_answer(row['question'], context_sentences)
            f1 = compute_f1(row['text'], predicted_answer)
            f1_values.append(f1)
        
        print(f"F1 score: {mean(f1_values)}")
            