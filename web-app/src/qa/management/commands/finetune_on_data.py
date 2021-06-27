from django.core.management.base import BaseCommand

from haystack.reader.farm import FARMReader

from src.qa.models import Document

ROBERTA_BASE_MODEL = "deepset/roberta-base-squad2"
MINILM_UNCASED_MODEL = "deepset/minilm-uncased-squad2"

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        input_data_path = '/app/static/'
        reader = FARMReader(model_name_or_path=MINILM_UNCASED_MODEL)
        reader.train(data_dir=input_data_path, train_filename="output-train.squad.json", n_epochs=1, save_dir="finetuned_model/minilm")

        
        