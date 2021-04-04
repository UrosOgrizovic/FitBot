from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from src.qa.apps import QaConfig

# Create your views here.


class QAView(APIView):
    """
        Search artwork database view.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
            API endpoint that allows user to search for artwork.
        """

        question = request.data.get('question', None)
        if not question:
            return Response({'error': 'Question was not passed in request body.'}, status=status.HTTP_400_BAD_REQUEST)

        prediction = QaConfig.pipe.run(query=question, top_k_retriever=10, top_k_reader=5)
        print(prediction)

        return render(request, 'qa/index.html', prediction)

        # return Response(data=prediction, status=status.HTTP_200_OK)


def index(request):
    return render(request, 'qa/index.html', {})