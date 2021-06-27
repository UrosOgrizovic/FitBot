import nlpaug.augmenter.word as naw
from nltk import tokenize

from django.core.management.base import BaseCommand

from src.qa.models import Document

translator_augmenters = [
    naw.BackTranslationAug(
        from_model_name='facebook/wmt19-en-de', 
        to_model_name='facebook/wmt19-de-en'
    ),
    naw.BackTranslationAug(
        from_model_name='facebook/wmt19-en-ru', 
        to_model_name='facebook/wmt19-ru-en'
    )
]

class Command(BaseCommand):
    def lazy_bulk_fetch(self, max_obj, max_count, fetch_func, start=0):
        counter = start
        while counter < max_count:
            yield fetch_func()[counter:counter + max_obj]
            counter += max_obj

    def handle(self, *args, **kwargs):
        q = Document.objects.all()

        fetcher = self.lazy_bulk_fetch(1000, q.count(), lambda: q)
        for batch in fetcher:
            for obj in batch:
                for augmenter in translator_augmenters:
                    is_different = False
                    new_sentences = []
                    for sentence in tokenize.sent_tokenize(obj.text):
                        new_text = augmenter.augment(sentence)
                        if new_text != sentence:
                            is_different = True
                        new_sentences.append(new_text)

                    if not is_different:
                        continue
                    
                    Document.objects.create(text=new_sentences.join(' '))
