from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path("account_manage/", AccountManage.as_view(), name="AccountManage"),
    # path("<uid>", AdminView.as_view(), name="AdminView"),
    path("doc_data_manage/", DocDataView.as_view(),name="DocDataView"),
]
