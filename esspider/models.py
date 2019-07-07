from django.db import models
from django.utils import timezone

# Create your models here.
class DocData(models.Model):

    doc_dict = models.TextField()
    uuid = models.CharField(max_length=255,blank=True,null=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = '文档数据表'
        verbose_name_plural = '文档数据表'
        ordering = ['-id', ]  # 防止rest_framework.PageNumberPagination 报错


    def __str__(self):
        return '文档数据 %d %s' % (self.id, self.uuid)

class Account(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = '模拟登陆用户表'
        verbose_name_plural = '模拟登陆用户表'
        ordering = ['id', ]  # 防止rest_framework.PageNumberPagination 报错


    def __str__(self):
        return '用户数据 %s %s' % (self.username, self.is_active)
