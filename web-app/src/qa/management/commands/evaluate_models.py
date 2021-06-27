from django.core.management.base import BaseCommand

from haystack.reader.farm import FARMReader
from farm.utils import initialize_device_settings

from src.qa.models import Document

device, n_gpu = initialize_device_settings(use_cuda=True)

ROBERTA_BASE_MODEL = "deepset/roberta-base-squad2"
MINILM_UNCASED_MODEL = "deepset/minilm-uncased-squad2"
BERT_BASE_MODEL = "distilbert-base-uncased-distilled-squad"

ROBERTA_FINETUNED = "finetuned_model/roberta"
MINILM_FINETUNED = "finetuned_model/minilm"

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        input_data_path = '/app/static/'
        # reader_roberta = FARMReader(model_name_or_path=ROBERTA_BASE_MODEL)
        # reader_eval_results_base_roberta = reader_roberta.eval_on_file(input_data_path, "output-test.squad.json", device=device)

        reader_roberta = FARMReader(model_name_or_path=MINILM_FINETUNED)
        reader_eval_results_finetuned_roberta = reader_roberta.eval_on_file(input_data_path, "output-test.squad.json", device=device)
        # print(f"BASE ROBERTA: {reader_eval_results_base_roberta}")
        print(f"FINETUNED ROBERTA: {reader_eval_results_finetuned_roberta}")

        # input_data_path = '/app/static/nq/'
        # reader = FARMReader(model_name_or_path=MINILM_FINETUNED)
        # reader_eval_results_base = reader.eval_on_file(input_data_path, "nq_dev_subset_v2.json", device=device)

        # reader_roberta = FARMReader(model_name_or_path=ROBERTA_FINETUNED)
        # reader_eval_results_finetuned_roberta = reader_roberta.eval_on_file(input_data_path, "nq_dev_subset_v2.json", device=device)
        # print(f"BASE: {reader_eval_results_base}")
        # print(f"FINETUNED ROBERTA: {reader_eval_results_finetuned_roberta}")

        # reader_eval_results = reader.eval_on_file(input_data_path, "output-test.squad.json", device=device)


