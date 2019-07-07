from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path("", AdminView.as_view(), name="AdminView"),
    # path("<uid>", AdminView.as_view(), name="AdminView"),
    path("comment/",CommentView.as_view(),name="CommentView"),
    path("comment/<uuid>",CommentView.as_view(),name="CommentView"),
    path("manage/",ManageDocView.as_view(),name="ManageDocView"),
    path("manage/<doc>",ManageDocView.as_view(),name="ManageDocView"),
    path("register/",Register.as_view(), name="Register"),
    path("register/<token>",Register.as_view(), name="Register"),
    path("login/",UserLogin.as_view(),name="UserLogin"),
    path("comment_manage/",CommentManageView.as_view(),name="CommentManageView"),
    path("comment_manage/<uuid>",CommentManageView.as_view(),name="CommentManageView"),
    path("user_manage/", UserManageView.as_view(), name="UserManageView"),
    path("user_manage/<uid>", UserManageView.as_view(), name="UserManageView")
]
