from es_django import celery_app as app
from django.core.cache import cache
import requests
import os
from esspider.utils.pdf2txt import *
from esspider.utils.txt2dict import *
from .models import *
from esspider.utils.update_pdf import *
from esspider.utils.text_proxies import *

@app.task(bind=True)
def temp(self):
    print("hello")


@app.task(bind=True)
def get_doc(self,uuid):
    pdf_url_1 = 'https://www.jufaanli.com/home/download/handlePdf?uuid='
    pdf_url_2 = '&keyword=%E4%B8%AA%E4%BA%BA%E4%B8%AD%E5%BF%83'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    sess = requests.session()
    cookies = cache.get("pdf_cookies")
    if not cookies:
        account = Account.objects.filter(is_active=True).first()
        cookies = login_new(user=account.username,password=account.password)
        cache.set("pdf_cookies", cookies, 60 * 60 * 5)
    # 拿到cookies
    sess.cookies = cookies
    pdf_url = pdf_url_1 + uuid + pdf_url_2
    res = sess.get(pdf_url, headers=headers)
    pdf_path = os.getcwd() + "/esspider/pdf_data"
    # 保存pdf文件
    with open(pdf_path + '/' + uuid + '.pdf', 'wb') as f:
        f.write(res.content)
    # 将pdf二进制数据转为txt
    txt = readPDF(open(pdf_path + '/' + uuid + '.pdf',"rb"))
    time.sleep(5)
    print(txt)
    dict_json = open_text_new(uuid=uuid,text=txt,root=os.getcwd()+"/esspider")
    title = get_title_new(txt)
    update_pdf(uuid=uuid,text_tilte=title,root=os.getcwd()+"/esspider/pdf_data/")
    DocData.objects.create(doc_dict=dict_json,uuid=uuid)



# 0f6cc9d559953147420203e1da180e93