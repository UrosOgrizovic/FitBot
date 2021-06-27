from django.core.management.base import BaseCommand
from django.conf import settings


import os
import re
import nltk
from lxml import etree
from lxml.etree import tostring
from unidecode import unidecode
from string import printable
from collections import Counter

from src.qa.models import Document
from src.qa.apps import QaConfig
from src.qa.management.commands.preprocess_utility import PreprocessUtility


class Command(BaseCommand, PreprocessUtility):
    def read_data(self, input_file_path):
        document_dictionaries = []
        # iterate through all lines

        with open(input_file_path, 'r') as f:
            workout_exercises = f.readlines()
        
        for exercise_sentence in workout_exercises:
            if QaConfig.retriever_type == 'sparse':
                document_dictionaries.append({'text': exercise_sentence, 'meta': None})
                continue

            text_splits = self.split_by_sentence_boundary(exercise_sentence)
            for text in text_splits:
                document_dictionaries.append({'text': text, 'meta': None})

        return self.process_documents(document_dictionaries)

    def handle(self, *args, **kwargs):
        input_file_path = os.path.join(settings.STATIC_ROOT, 'workout_sentences.txt')
        document_dictionaries = self.read_data(input_file_path)

        for document in document_dictionaries:
            Document.objects.create(text=document.get('text', ''))

