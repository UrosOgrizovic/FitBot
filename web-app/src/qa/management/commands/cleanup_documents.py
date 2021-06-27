from django.core.management.base import BaseCommand

from src.qa.documents import Document, Keyword, Keyphase

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        count, _ = Document.objects.filter(text='').delete()
        print(f"Deleted {count} number of documents that are empty.")

        count, _ = Document.objects.filter(keywords__isnull=True).delete()
        print(f"Deleted {count} number of documents that are empty.")

        # Keyword.objects.values_list('text').annotate(keyword_count=Count('text')).order_by('keyword_count')
        keywords = Keyword.objects.values_list('text').annotate(keyword_count=Count('text')).filter(keyword_count__lte=3).order_by('keyword_count')
        for keyword, occurance in keywords:
            print(keyword, occurance)
