import newspaper
import pandas as pd

from newspaper import Article, Source
from string import printable

from django.core.management.base import BaseCommand
from django.conf import settings

from src.qa.management.commands.preprocess_utility import PreprocessUtility
from src.qa.models import Document, Keyphrase, Keyword

WEBSITES_TO_SCRAPE = [
    {'name': 'musleandfitness-nutrition', 'url': 'https://muscleandfitness.com/nutrition/'},
    {'name': 'fitnesspalweightloss', 'url': 'https://blog.myfitnesspal.com/category/weight-loss/'},
    {'name': 'nerdfitness-blog', 'url': 'https://www.nerdfitness.com/blog/'},
    {'name': 'rosstraining-blog', 'url': 'http://rosstraining.com/blog/'},
    {'name': 'lovesweatfitness', 'url': 'https://lovesweatfitness.com/blog/'},
    {'name': 'breakingmuscle-fitness', 'url': 'https://breakingmuscle.com/fitness'},
    {'name': 'advancedhumanperformance-blog', 'url': 'https://www.advancedhumanperformance.com/blog'},
    {'name': 'tonygentilcore-blog', 'url': 'https://tonygentilcore.com/blog/'},
    {'name': 'drjohnrusin-blog', 'url': 'https://drjohnrusin.com/blog/'},
    {'name': 'balancedlifeonline-blog', 'url': 'https://thebalancedlifeonline.com/blog/'},
    {'name': 'knockedupfitness-blog', 'url': 'https://knocked-upfitness.com/blog/'},
    {'name': 'bengreenfieldfitness-blog', 'url': 'https://bengreenfieldfitness.com/'},
    {'name': 'gethealthyu-blog', 'url': 'https://gethealthyu.com/fitness/'},
    {'name': 'keepitsimpelle-blog', 'url': 'https://www.keepitsimpelle.com/search/label/fitness/'},
    {'name': 'stephgaudreau-blog', 'url': 'https://www.stephgaudreau.com/'}
]

class Command(BaseCommand, PreprocessUtility):
    def handle(self, *args, **kwargs):
        Document.objects.all().delete()
        Keyphrase.objects.all().delete()
        Keyword.objects.all().delete()

        for website in WEBSITES_TO_SCRAPE:
            scraper = newspaper.build(website['url'], memoize_articles=False)
            document_dictionaries = []

            print(f"Found {len(scraper.articles)} number of articles on {website['name']}.")

            for article in scraper.articles:
                try:
                    article.download()
                    article.parse()
                except:
                    continue

                document_dictionaries.append({'text': article.text, 'meta': None})

                text_splits = self.split_by_sentence_boundary(article.text)
                for text in text_splits:
                    document_dictionaries.append({'text': text, 'meta': None})

            processed_document_dictionaries = self.process_documents(document_dictionaries)
            for document in document_dictionaries:
                Document.objects.create(text=document.get('text', ''))
            
            print(f"Website {website['name']} is done downloading.")
