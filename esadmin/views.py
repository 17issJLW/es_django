from django.shortcuts import render
from django.core.mail import send_mail
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from lib.rest_framework.util import *
from django.db import transaction
from lib.rest_framework.exceptions import *
import datetime
import requests
import json
import base64
from rest_framework.pagination import PageNumberPagination
from lib.rest_framework.permissions import *
from rest_framework import status
# Create your views here.
class Pagination(PageNumberPagination):
    """
    配置分页规则
    """
    page_size = 20                          #每页显示数目
    page_size_query_param = 'size'          #控制每页显示数目的参数
    page_query_param = 'page'               #获得页数的参数
    max_page_size = 100                     #每页最大显示数目


class AdminView(APIView):


    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.filter(username=serializer.validated_data["username"],
                                password=serializer.validated_data["password"],
                                role__role_name="admin",
                                is_active=True).first()
            if user:
                payload = {"type": "", "username": "","uid":str(user.uid)}
                payload["type"] = user.role.role_name
                payload["username"] = user.username
                token = create_jwt(payload)
                return Response({"token":token,
                                 "username":user.username,
                                 "type":user.role.role_name,
                                 "uid": str(user.uid)})
            else:
                raise PermissionDeny

    @check_admin_token
    def get(self,request):
        uid = request.META.get("REMOTE_USER").get("uid")
        user = User.objects.filter(uid=uid).first()
        serializer = UserSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @check_admin_token
    @transaction.atomic()
    def put(self,request):
        my_uid = request.META.get("REMOTE_USER").get("uid")
        user = User.objects.filter(uid=my_uid).first()
        if(user):
            if(request.data.get("password")):
                user.password = request.data.get("password")
            if(request.data.get("email")):
                user.email = request.data.get("email")
            user.save()
            return Response({"ok"}, status=status.HTTP_200_OK)
        else:
            raise NotFound

class ManageDocView(APIView):

    # sess = requests.session()
    headers = {
        "Content-Type":'application/json',
    }
    base_url = settings.ES_SPRING

    @check_admin_token
    def post(self, request):
        data = request.data
        r = requests.post(self.base_url+"doc/manage/",data=json.dumps(data),headers=self.headers)
        return Response(r.content,status=r.status_code)

    @check_admin_token
    def put(self,request,doc):
        data = request.data
        r = requests.put(self.base_url+"doc/manage/"+str(doc),data=json.dumps(data),headers=self.headers)
        return Response(r.content, status=r.status_code)

    @check_admin_token
    def delete(self,request,doc):
        r = requests.delete(self.base_url+"doc/manage/"+str(doc),headers=self.headers)
        return Response(r.content, status=r.status_code)


class CommentManageView(APIView):

    @check_admin_token
    def get(self,request):
        data = request.GET
        print(data)
        queryset = Comment.objects.all()
        if data.get("doc"):
            queryset = queryset.filter(doc=data.get("doc"))
        if data.get("user"):
            queryset = queryset.filter(user__uid=data.get("user"))
        if data.get("from_date") and data.get("to_date"):
            queryset = queryset.filter(date__gte=datetime.datetime.strptime(data.get("from_date"),"%Y-%m-%d"))\
                .filter(date__lte=datetime.datetime.strptime(data.get("to_date"),"%Y-%m-%d"))
        page = Pagination()
        result = page.paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = CommentSerializer(result, many=True)
        return page.get_paginated_response(serializer.data)


    @check_admin_token
    @transaction.atomic()
    def post(self,request):
        print("comment post")
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True) and request.data.get("user"):
            data = serializer.validated_data
            user = User.objects.filter(uid=request.data.get("user")).first()
            if not user:
                raise NotFound
            Comment.objects.create(
                doc=data.get("doc"),
                text=data.get("text"),
                is_anonymous=data.get("is_anonymous"),
                user=user
            )
            return Response(request.data,status=status.HTTP_200_OK)
        raise BadRequest

    @check_admin_token
    @transaction.atomic()
    def put(self,request,uuid):
        comment = Comment.objects.filter(uuid=uuid).first()
        if comment:
            serializer = CommentSerializer(comment,data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                serializer.save()
                return Response(data,status=status.HTTP_200_OK)

        raise NotFound

    @check_admin_token
    def delete(self,request,uuid):
        comment = Comment.objects.filter(uuid=uuid).first()
        if comment:
            comment.delete()
            return Response({"ok"},status=status.HTTP_200_OK)
        raise NotFound

class UserManageView(APIView):

    @check_admin_token
    def get(self,request):
        data = request.GET
        queryset = User.objects.all()
        if data.get("username"):
            queryset = queryset.filter(username__icontains=data.get("username"))
        if data.get("role_name"):
            queryset = queryset.filter(role__role_name=data.get("role_name"))
        if data.get("is_active"):
            queryset = queryset.filter(is_active=data.get("is_active"))
        page = Pagination()
        result = page.paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = UserSerializer(result, many=True)
        return page.get_paginated_response(serializer.data)

    @check_admin_token
    @transaction.atomic()
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True) and request.data.get("role_name"):
            role = Roles.objects.filter(role_name=request.data.get("role_name")).first()
            if not role:
                raise NotFound
            User.objects.create(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
                email=serializer.validated_data["email"],
                is_active=serializer.validated_data["is_active"],
                role=role
            )
            return Response(request.data,status=status.HTTP_200_OK)
        raise BadRequest


    @check_admin_token
    @transaction.atomic()
    def put(self,request,uid):
        user = User.objects.filter(uid=uid).first()
        if not user:
            raise NotFound
        serializer = UserSerializer(user,data=request.data)
        if serializer.is_valid(raise_exception=True):
            if request.data.get("role_name"):
                role = Roles.objects.filter(role_name=request.data.get("role_name")).first()
                if not role:
                    raise NotFound
                user.role = role
                user.username = serializer.validated_data["username"]
                user.password = serializer.validated_data["password"]
                user.email = serializer.validated_data["email"]
                user.is_active = serializer.validated_data["is_active"]
                user.save()
            else:
                print(serializer.validated_data)
                serializer.save()
            return Response(request.data,status=status.HTTP_200_OK)
        raise BadRequest

    @check_admin_token
    def delete(self,request,uid):
        user = User.objects.filter(uid=uid).first()
        if not user:
            raise NotFound
        user.delete()
        return Response({"ok"},status=status.HTTP_200_OK)



class Register(APIView):

    @transaction.atomic()
    def post(self,request):

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            role = Roles.objects.get(role_name="user")
            user = User.objects.create(
                username=data["username"],
                password=data["password"],
                role=role,
                email=data["email"],
                is_active=False
            )
            encodeuid = base64.b64encode(str(user.uid).encode('utf-8'))
            send_mail(subject="【CJ Search】邮箱验证", message="", from_email=settings.EMAIL_FROM, recipient_list=[data["email"]],
                      html_message=settings.EMAIL_HTML.format(str(encodeuid,"utf8"),str(encodeuid,"utf8")))
            return Response({
                             "username": user.username,
                             "type": user.role.role_name,
                             "uid": str(user.uid)},status=status.HTTP_200_OK)
        raise BadRequest


    def get(self,request,token):
        decodeb = token.encode("utf-8")
        decodestr = base64.b64decode(decodeb)
        print(decodestr)
        user = User.objects.filter(uid=str(decodestr, "utf8")).first()
        if not user:
            raise NotFound
        user.is_active = True
        user.save()
        payload = {"type": "", "username": "", "uid": str(user.uid)}
        payload["type"] = user.role.role_name
        payload["username"] = user.username
        token = create_jwt(payload)
        return Response({
            "token": token,
            "username": user.username,
            "type": user.role.role_name,
            "uid": str(user.uid)}, status=status.HTTP_200_OK)



class UserLogin(APIView):

    @transaction.atomic()
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.filter(username=serializer.validated_data["username"],
                                       password=serializer.validated_data["password"]
                                       ).first()
            if user:
                if user.is_active == False:
                    raise PermissionDeny
                payload = {"type": "", "username": "", "uid": str(user.uid).replace("-", '')}
                payload["type"] = user.role.role_name
                payload["username"] = user.username
                token = create_jwt(payload)
                return Response({"token": token,
                                 "username": user.username,
                                 "type": user.role.role_name,
                                 "uid": str(user.uid).replace("-", '')})
            raise PasswordError
        raise BadRequest

    @check_token
    def get(self, request):
        uid = request.META.get("REMOTE_USER").get("uid")
        user = User.objects.filter(uid=uid).first()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @check_token
    @transaction.atomic()
    def put(self, request):
        my_uid = request.META.get("REMOTE_USER").get("uid")
        user = User.objects.filter(uid=my_uid).first()
        if user:
            if request.data.get("password"):
                user.password = request.data.get("password")
            if request.data.get("email"):
                user.email = request.data.get("email")
            user.save()
            return Response({"ok"}, status=status.HTTP_200_OK)
        else:
            raise NotFound



class CommentView(APIView):

    def get(self,request,uuid):
        queryset = Comment.objects.filter(doc=uuid)
        page = Pagination()
        result = page.paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = CommentSerializer(result, many=True)
        return page.get_paginated_response(serializer.data)

    @check_token
    @transaction.atomic()
    def post(self,request):
        my_uid = request.META.get("REMOTE_USER").get("uid")
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            user = User.objects.filter(uid=my_uid).first()
            if not user:
                raise NotFound
            comment = Comment.objects.create(
                text=data.get("text"),
                doc=data.get("doc"),
                is_anonymous=data.get("is_anonymous"),
                user=user
            )
            return Response({"ok"},status=status.HTTP_200_OK)
        raise BadRequest


    @check_token
    @transaction.atomic()
    def put(self, request, uuid):
        my_uid = request.META.get("REMOTE_USER").get("uid")
        comment = Comment.objects.filter(user__uid=my_uid,uuid=uuid).first()
        if not comment:
            raise NotFound
        serializer = CommentSerializer(comment,data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            serializer.save()
            return Response(data, status=status.HTTP_200_OK)
        raise BadRequest

    @check_token
    def delete(self,request,uuid):
        my_uid = request.META.get("REMOTE_USER").get("uid")
        comment = Comment.objects.filter(user__uid=my_uid, uuid=uuid).first()
        if comment:
            comment.delete()
            return Response({"ok"},status=status.HTTP_200_OK)
        raise NotFound

class RoleView(APIView):

    @check_admin_token
    def get(self,request):
        roles = Roles.objects.all()
        serializer = RoleSerializer(roles,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @check_admin_token
    def post(self,request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"ok"},status=status.HTTP_200_OK)
        raise BadRequest

