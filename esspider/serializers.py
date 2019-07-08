from rest_framework import serializers
from .models import *

class DocDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocData
        fields = "__all__"

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = "__all__"