import matplotlib.pyplot as plt
import seaborn as sns
import spacy

from collections import Counter, defaultdict

from django.core.management.base import BaseCommand
from django.conf import settings

from nltk.corpus import stopwords

from src.qa.models import Document

class Command(BaseCommand):
    def lazy_bulk_fetch(self, max_obj, max_count, fetch_func, start=0):
        counter = start
        while counter < max_count:
            yield fetch_func()[counter:counter + max_obj]
            counter += max_obj

    def handle(self, *args, **kwargs):
        nlp = spacy.load('en_core_web_sm')
        def _get_ner(text):
            doc=nlp(text)
            return [X.label_ for X in doc.ents]

        q = Document.objects.all()
        stop = set(stopwords.words('english'))

        fetcher = self.lazy_bulk_fetch(1000, q.count(), lambda: q)
        stop_words = defaultdict(int)
        words = []
        ents = []
        for batch in fetcher:
            for obj in batch:
                all_document_words = obj.text.split(" ")
                words.extend(all_document_words)
                for word in all_document_words:
                    if word in stop:
                        stop_words[word] += 1
                ents.append(_get_ner(obj.text))
        
        ents = [x for sub in ents for x in sub]
        counter = Counter(ents)
        count = counter.most_common()
        x,y=map(list, zip(*count))
        sns.barplot(x=y,y=x)
        plt.show()
        return

                        
        top = sorted(stop_words.items(), key= lambda x:x[1], reverse=True)[:10]
        x, y = zip(*top)
        # plt.bar(x, y) # plotting frequency of stop words
        # plt.show()

        counter = Counter(words)
        most = counter.most_common()

        x, y = [], []
        for word, count in most:
            if word not in stop:
                x.append(word)
                y.append(count)
            
            if len(x) > 40:
                break
        
        # sns.barplot(x=y, y=x)
        # plt.show()

        

