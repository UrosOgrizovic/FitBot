from django.conf.urls import url
from django.urls import path

from src.qa.views import QAView, index


api_urlpatterns = [
    url('questions/', QAView.as_view(), name='ask')
]

urlpatterns = [
    path('questions', index, name='index')
]
