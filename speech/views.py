from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import *

# Create your views here.
class SpeechRecognition(APIView):

    def post(self,request):
        request_data = request.data
        file = request_data.get("file")
        file2 = request_data.get("file2")
        print(file2)
        print(file)
        with open("temp.wav","wb") as f:
            f.write(file.read())

        try:
            res = audio_recognition("temp.wav")
        except:
            return Response({"error":"Could not understand audio"},status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response({"result":res},status=status.HTTP_200_OK)


# class Spider(APIView):
#
#     def get(self,request):

