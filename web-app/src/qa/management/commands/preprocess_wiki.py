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
        tree = etree.parse(input_file_path)
        root = tree.getroot()

        document_dictionaries = []
        # iterate through all the titles
        for text_node in root.findall(".//text", namespaces=root.nsmap):
            if QaConfig.retriever_type == 'sparse':
                document_dictionaries.append({'text': text_node.text, 'meta': None})
                continue

            text_splits = self.split_by_sentence_boundary(text_node.text)
            for text in text_splits:
                document_dictionaries.append({'text': text, 'meta': None})

        return self.process_documents(document_dictionaries)

    def handle(self, *args, **kwargs):
        Document.objects.all().delete()

        input_file_path = os.path.join(settings.STATIC_ROOT, 'Wikipedia-Strength-Training.xml')
        document_dictionaries = self.read_data(input_file_path)

        for document in document_dictionaries:
            Document.objects.create(text=document.get('text', ''))

