from django.apps import AppConfig
from django.conf import settings
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.reader.farm import FARMReader
from haystack.pipeline import ExtractiveQAPipeline


class QaConfig(AppConfig):
    name = 'src.qa'

    document_store = ElasticsearchDocumentStore(host=settings.ELASTICSEARCH_HOST, username="", password="", index="document")
    retriever = ElasticsearchRetriever(document_store=document_store)
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)
    pipe = ExtractiveQAPipeline(reader, retriever)
