from django.apps import AppConfig
from django.conf import settings

# from keybert import KeyBERT
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.retriever.dense import DensePassageRetriever
from haystack.reader.farm import FARMReader
from haystack.pipeline import ExtractiveQAPipeline
ROBERTA_BASE_MODEL = "deepset/roberta-base-squad2"
MINILM_UNCASED_MODEL = "deepset/minilm-uncased-squad2"

ROBERTA_FINETUNED = "finetuned_model/roberta"
MINILM_FINETUNED = "finetuned_model/minilm"

# KEYWORD_MODEL = "distilbert-base-nli-mean-tokens"

class QaConfig(AppConfig):
    name = 'src.qa'

    document_store = ElasticsearchDocumentStore(host=settings.ELASTICSEARCH_HOST, username="", password="", index="document")
    reader = FARMReader(model_name_or_path=ROBERTA_FINETUNED, use_gpu=True)
    retriever = DensePassageRetriever(document_store=document_store,
                                      query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
                                      passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
                                      max_seq_len_query=64,
                                      max_seq_len_passage=256,
                                      batch_size=16,
                                      use_gpu=False,
                                      embed_title=True,
                                      use_fast_tokenizers=True)
    pipe = ExtractiveQAPipeline(reader, retriever)

    retriever_type = 'dense' if isinstance(retriever, DensePassageRetriever) else 'sparse'
    # kw_model = KeyBERT(KEYWORD_MODEL)
