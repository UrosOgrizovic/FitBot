'''
    Command to create output txt file containing document paragraphs that are input to the QA generator.
'''
from django.core.management.base import BaseCommand

from src.qa.models import Document

class Command(BaseCommand):
    def lazy_bulk_fetch(self, max_obj, max_count, fetch_func, start=0):
        counter = start
        while counter < max_count:
            yield fetch_func()[counter:counter + max_obj]
            counter += max_obj

    def handle(self, *args, **kwargs):
        output_path = '/app/static/output-train.txt'
        q = Document.objects.filter(train=True)

        fetcher = self.lazy_bulk_fetch(1000, q.count(), lambda: q)
        with open(output_path, 'a') as f:
            for batch in fetcher:
                for obj in batch:
                    f.write(obj.text)
                    f.write("\n")
        