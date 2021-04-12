from django.contrib import admin

from src.qa.models import Document

# Register your models here.

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass
