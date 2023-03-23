from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.


class TestView(APIView):
    # getting information from the server
    def get(self, request, format=None):
        print("API was Called")
        return Response("You Made It", status=200)

    # send something to django create object
    # def post():
        # ...

    # send something to django to update object
    # def put():
        # ...
