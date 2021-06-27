import random

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from src.common.models import TimeStampedModel
from src.qa.apps import QaConfig

# Create your models here.

class Document(TimeStampedModel):
    """
    A model class used for storing one text document.
    """
    text = models.TextField(null=True, blank=True)
    train = models.BooleanField(default=True)

    def __str__(self):
        if self.text:
            return f'{self.text[:20]}...'
        return 'Document'


class Keyword(TimeStampedModel):
    """
    A model class used for storing keyword of a document.
    """
    text = models.CharField(max_length=100)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='keywords')
    
    def __str__(self):
        if self.text:
            return self.text
        return 'Keyword'

class Keyphrase(TimeStampedModel):
    """
    A model class used for storing keyphrase of a document.
    """
    text = models.CharField(max_length=100)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='keyphrases')

    def __str__(self):
        if self.text:
            return self.text
        return 'Keyphrase'

class DocumentMetaEntry(TimeStampedModel):
    """
    A model class used for adding additional document information.
    """
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='meta')

@receiver(post_save, sender=Document)
def add_keywords_to_document(sender, instance, created, **kwargs):
    if created:
        keyphrases = QaConfig.kw_model.extract_keywords(instance.text, keyphrase_ngram_range=(3, 3), stop_words='english', use_mmr=True, diversity=0.4)
        keywords = QaConfig.kw_model.extract_keywords(instance.text, keyphrase_ngram_range=(1, 1), stop_words=None)

        for keyword, prob in keywords:
            Keyword.objects.create(text=keyword, document=instance)

        for keyphrase, prob in keyphrases:
            Keyphrase.objects.create(text=keyword, document=instance)
        
        instance.train = random.randint(1, 100) > 20
        instance.save()

    
