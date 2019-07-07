from django.db import models
from django.utils import timezone
import uuid

# Create your models here.
class User(models.Model):
    uid = models.UUIDField(verbose_name="用户id",primary_key=True,auto_created=True,default=uuid.uuid4, editable=False)
    username = models.CharField(verbose_name="用户名",max_length=32,unique=True)
    password = models.CharField(verbose_name="用户密码",max_length=128)
    email = models.EmailField(verbose_name="邮箱")
    role = models.ForeignKey("Roles", on_delete=models.CASCADE,default=None)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = '用户表'
        ordering = ['uid', ]  # 防止rest_framework.PageNumberPagination 报错


    def __str__(self):
        return '用户 %s %s' % (self.uid, self.username)

class Roles(models.Model):
    ROLE_NAME=(
        ("admin","admin"),
        ("user","user")
    )
    role_name = models.CharField(verbose_name="角色名",max_length=32)

    class Meta:
        verbose_name = '角色表'
        verbose_name_plural = '角色表'
        ordering = ['id',]

    def __str__(self):
        return '%s' % (self.role_name)


class Comment(models.Model):
    uuid = models.UUIDField(primary_key=True,auto_created=True,default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey("User",on_delete=models.CASCADE)
    doc = models.CharField(max_length=64)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        verbose_name = '评论表'
        verbose_name_plural = '评论表'
        ordering = ['uuid', ]  # 防止rest_framework.PageNumberPagination 报错

    def __str__(self):
        return '%s 评论 %s' % (self.user.username, self.text)
