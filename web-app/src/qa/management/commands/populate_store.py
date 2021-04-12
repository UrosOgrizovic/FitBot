from django.core.management.base import BaseCommand

from src.qa.models import Document
from src.qa.apps import QaConfig


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
            document_dictionaries = []
            for obj in batch:
                document_dictionaries.append({'text': obj.text, 'meta': None})

            QaConfig.document_store.write_documents(document_dictionaries)

            QaConfig.document_store.update_embeddings(QaConfig.retriever)


