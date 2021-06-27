import nlpaug.augmenter.word as naw
from nltk import tokenize

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        questions = [
            "What is the best fitness exercise for biceps?",
            "How to build strong core?",
            "What is stamina?",
            "What is whey protein?",
            "How to get more muscle mass?",
            "What is muscle hypertrophy?",
            "How to get quickly shredded for summer?"
        ]
        aug = naw.SynonymAug(aug_src='wordnet')
        for question in questions:
            augmented_text = aug.augment(question)
            print("Original:")
            print(question)
            print("Augmented Text:")
            print(augmented_text)