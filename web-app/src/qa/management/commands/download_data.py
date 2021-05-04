import newspaper
import pandas as pd

from newspaper import Article, Source
from string import printable

from django.core.management.base import BaseCommand
from django.conf import settings

from src.qa.management.commands.preprocess_utility import PreprocessUtility
from src.qa.apps import QaConfig
from src.qa.models import Document


WEBSITES_TO_SCRAPE = [
    {'name': 'musleandfitness-nutrition', 'url': 'https://muscleandfitness.com/nutrition/'},
    {'name': 'musleandfitness-nutrition-healthy', 'url': 'https://muscleandfitness.com/nutrition/healthy-eating/'},
    {'name': 'musleandfitness-nutrition-lose-fat', 'url': 'https://muscleandfitness.com/nutrition/lose-fat/'},
    {'name': 'musleandfitness-nutrition-gain-mass', 'url': 'https://muscleandfitness.com/nutrition/gain-mass/'},
    {'name': 'musleandfitness-nutrition-supplements', 'url': 'https://muscleandfitness.com/supplements/'},
    {'name': 'musleandfitness-workouts', 'url': 'https://muscleandfitness.com/workouts/'},
    {'name': 'musleandfitness-workout-routines', 'url': 'https://muscleandfitness.com/workout-routines/'},
    {'name': 'musleandfitness-workout-tips', 'url': 'https://muscleandfitness.com/workouts/workout-tips/'},
    {'name': 'musleandfitness-fitness-essentials', 'url': 'https://muscleandfitness.com/fitness-essentials/'},
    {'name': 'musleandfitness-celebrity', 'url': 'https://muscleandfitness.com/workouts/athletecelebrity-workouts/'},
]

class Command(BaseCommand, PreprocessUtility):
    def handle(self, *args, **kwargs):
        for website in WEBSITES_TO_SCRAPE:
            scraper = newspaper.build(website['url'], memoize_articles=False)
            document_dictionaries = []

            print(f"Found {len(scraper.articles)} number of articles on {website['name']}.")

            for article in scraper.articles:
                article.download()
                article.parse()

                if QaConfig.retriever_type == 'sparse':
                    document_dictionaries.append({'text': article.text, 'meta': None})
                    continue

                text_splits = self.split_by_sentence_boundary(article.text)
                for text in text_splits:
                    document_dictionaries.append({'text': text, 'meta': None})

            processed_document_dictionaries = self.process_documents(document_dictionaries)
            for document in processed_document_dictionaries:
                Document.objects.create(text=document.get('text', ''))
