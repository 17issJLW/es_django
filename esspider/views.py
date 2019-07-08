from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from lib.rest_framework.permissions import *
from .serializers import *
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


class DocDataView(APIView):

    @check_admin_token
    def get(self,request):
        queryset = DocData.objects.all().order_by("-id")
        page = Pagination()
        result = page.paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = DocDataSerializer(result, many=True)
        return page.get_paginated_response(serializer.data)

    @check_admin_token
    def post(self,request):
        serializer = DocDataSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"ok"},status=status.HTTP_200_OK)
        raise BadRequest

    @check_admin_token
    def put(self,request,id):
        doc_data = DocData.objects.filter(id=id).first()
        if not doc_data:
            raise NotFound
        serializer = DocDataSerializer(doc_data,data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"ok"},status=status.HTTP_200_OK)
        raise BadRequest

    @check_admin_token
    def delete(self,request,id):
        doc_data = DocData.objects.filter(id=id).first()
        if not doc_data:
            raise NotFound
        doc_data.delete()
        return Response({"ok"},status=status.HTTP_200_OK)


class AccountManage(APIView):

    @check_admin_token
    def get(self, request):
        queryset = Account.objects.all().order_by("-id")
        page = Pagination()
        result = page.paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = AccountSerializer(result, many=True)
        return page.get_paginated_response(serializer.data)

    @check_admin_token
    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"ok"}, status=status.HTTP_200_OK)
        raise BadRequest

    @check_admin_token
    def put(self, request, id):
        account = Account.objects.filter(id=id).first()
        if not account:
            raise NotFound
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"ok"}, status=status.HTTP_200_OK)
        raise BadRequest

    @check_admin_token
    def delete(self, request, id):
        account = Account.objects.filter(id=id).first()
        if not account:
            raise NotFound
        account.delete()
        return Response({"ok"}, status=status.HTTP_200_OK)