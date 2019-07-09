from rest_framework import serializers
from .models import *

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=32)
    password = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("uid","username","role","email","is_active","password")
        depth = 1



class CommentSerializer(serializers.ModelSerializer):

    uuid = serializers.ReadOnlyField(read_only=True)
    date = serializers.ReadOnlyField(read_only=True)
    username= serializers.ReadOnlyField(source="user.username")
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"

    def get_user(self,obj):
        return str(obj.user.uid)




class RegisterSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = ("username","password","email")

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Roles
        fields = "__all__"