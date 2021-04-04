from django.db import models

from src.common.models import TimeStampedModel

# Create your models here.

class Document(TimeStampedModel):
    """
    A model class used for storing one text document.
    """
    text = models.TextField(null=True, blank=True)


class DocumentMetaEntry(TimeStampedModel):
    """
    A model class used for adding additional document information.
    """
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='meta')

