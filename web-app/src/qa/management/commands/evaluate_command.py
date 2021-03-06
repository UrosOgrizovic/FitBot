from django.core.management.base import BaseCommand

from src.qa.apps import QaConfig
from difflib import SequenceMatcher

ROBERTA_BASE_MODEL = "deepset/roberta-base-squad2"
MINILM_UNCASED_MODEL = "deepset/minilm-uncased-squad2"


class Command(BaseCommand):
    def read_evaluation_data(self, path="evaluation_data.txt"):
        questions, answers, contexts = [], [], []
        with open(path, "r") as f:
            content = f.readlines()[1:]  # skip header
            for line in content:
                question, answer, context = line.split("|")
                questions.append(question)
                answers.append(answer)
                contexts.append({"text": context})
        return questions, answers, contexts

    def get_similarities(self, questions, answers):
        similarities = []
        for i, question in enumerate(questions):
            print(question)
            prediction = QaConfig.pipe.run(query=question, top_k_retriever=3, top_k_reader=3)
            best_answer_obj = prediction['answers'][0]
            best_answer_txt = best_answer_obj['answer']
            best_answer_context = best_answer_obj['context']
            print('predicted ans', best_answer_txt, 'actual ans', answers[i])
            similarity = SequenceMatcher(None, best_answer_txt, answers[i]).ratio()
            if len(best_answer_txt.split(" ")) > 2 and (best_answer_txt in answers[i] or answers[i] in best_answer_txt):
                # increase similarity for exact matches
                similarity = min(1.0, similarity + 0.3)
            similarities.append(
                {'similarity': similarity, 'txt': best_answer_txt,
                 'context': best_answer_context})
        return similarities

    def handle(self, *args, **kwargs):
        questions, answers, contexts = self.read_evaluation_data()
        similarities = self.get_similarities(questions, answers)
        print('similarities', [sim['similarity'] for sim in similarities])
