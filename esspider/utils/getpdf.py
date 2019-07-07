import urllib
import requests
import time
import os
import json
from urllib.parse import quote

# 创建session对象
ssion = requests.session()

#  headers
# 请保证该cookie的来源 账号 不与爬取 uuid的混用
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'cookie': 't=b648ff4f227532bd8cdba0452bf0b56e; BJYSESSION=c7au0pimel449su1fko46ufg80; BJYSESSION=c7au0pimel449su1fko46ufg80; refer_url=http%3A%2F%2Fwww.jufadh.com%2F%3Fsrc%3Djufaanli.com; Hm_lvt_7d935fee641e9bdd8fd6b28e9a2b62dc=1561917031,1562068878,1562070603,1562082958; is_remember=0; login_time=2019-07-03+09%3A10%3A32; Hm_lpvt_7d935fee641e9bdd8fd6b28e9a2b62dc=1562116238; tf=b17de0557936a74b9ba3e19500e7ec22'
}

# 下载PDF的url部分
pdf_url_1 ='https://www.jufaanli.com/home/download/handlePdf?uuid='
pdf_url_2 ='&keyword=%E4%B8%AA%E4%BA%BA%E4%B8%AD%E5%BF%83'

def getpdf(uuid:str,path:str):
   pdf_url = pdf_url_1+uuid+pdf_url_2
   response = ssion.get(pdf_url, headers=headers)
   #print(response.content)
   with open(path+'/'+uuid + '.pdf', 'wb') as f:
      f.write(response.content)
   print("成功爬了")

# 测试
# uuid='1T4wXNMz'
# path ='.'
# getpdf(uuid=uuid,path=path)