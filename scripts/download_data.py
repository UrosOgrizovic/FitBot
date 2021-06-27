import newspaper
import pandas as pd

from newspaper import Article, Source
from string import printable

import preprocess_utility
import pickle
import time
import requests
import json
import concurrent.futures

WEBSITES_TO_SCRAPE = [
    {'name': 'musleandfitness-nutrition-lose-fat', 'url': 'https://muscleandfitness.com/nutrition/lose-fat/'},
    {'name': 'musleandfitness-nutrition-gain-mass', 'url': 'https://muscleandfitness.com/nutrition/gain-mass/'},
    {'name': 'musleandfitness-nutrition-supplements', 'url': 'https://muscleandfitness.com/supplements/'},
    {'name': 'musleandfitness-workouts', 'url': 'https://muscleandfitness.com/workouts/'},
    {'name': 'musleandfitness-workout-routines', 'url': 'https://muscleandfitness.com/workout-routines/'},
    {'name': 'musleandfitness-workout-tips', 'url': 'https://muscleandfitness.com/workouts/workout-tips/'},
    {'name': 'musleandfitness-fitness-essentials', 'url': 'https://muscleandfitness.com/fitness-essentials/'},
    {'name': 'musleandfitness-celebrity', 'url': 'https://muscleandfitness.com/workouts/athletecelebrity-workouts/'},
]


def download_data():
    processed_document_dictionaries = []
    contexts = []
    for website in WEBSITES_TO_SCRAPE:
        scraper = newspaper.build(website['url'], memoize_articles=False)
        document_dictionaries = []
        evaluation_data = []
        print(f"Found {len(scraper.articles)} number of articles on {website['name']}.")

        for article in scraper.articles:
            article.download()
            article.parse()

            document_dictionaries.append({'text': article.text, 'meta': None})

            text_splits = preprocess_utility.split_by_sentence_boundary(article.text)
            for text in text_splits:
                document_dictionaries.append({'text': text, 'meta': None})

        processed_document_dictionaries.append(preprocess_utility.process_documents(document_dictionaries))
        # questions_answers = get_answers_and_questions_for_context(processed_document_dictionaries[0]["text"])["result"]
        for processed in processed_document_dictionaries[0]:
            contexts.append(processed["text"])
    return processed_document_dictionaries, contexts


def get_answers_and_questions_for_context(context):
    url = "https://devpy.lumoslearning.com/llp/darshan/Jul20/question-answer-bert-gpt/question_generation/question_bert.php"
    headers = {
        'Content-Type': 'application/json'
    }
    response = json.loads(requests.post(url, headers=headers, data=json.dumps({"text": context})).text)
    if "error1" not in response.keys():
        response = {context: response}
    return response


def parallelize(contexts):
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_url = (executor.submit(get_answers_and_questions_for_context, context) for context in contexts)
        time1 = time.time()
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
            except Exception as exc:
                data = str(type(exc))
            finally:
                if "error1" not in data.keys():
                    print('data:', data)
                    out.append(data)
                print(str(len(out)), end="\r")
        time2 = time.time()
    print(f'getting questions and answers took: {time2 - time1} seconds')
    return out


if __name__ == '__main__':
    # start = time.time()
    # processed_document_dictionaries, contexts = download_data()
    # end = time.time()
    # print(f'downloading data took {end - start} seconds')
    # pickle.dump(contexts, open("contexts.pkl", "wb"))
    # pickle.dump(processed_document_dictionaries, open("data.pkl", "wb"))
    # contexts = pickle.load(open("contexts.pkl", "rb"))
    questions_answers = pickle.load(open("evaluation_data.pkl", "rb"))
    # questions_answers = parallelize(contexts)
    #  pickle.dump(questions_answers, open("evaluation_data.pkl", "wb"))
    print(len(questions_answers))
    # print(processed_document_dictionaries[:5])
