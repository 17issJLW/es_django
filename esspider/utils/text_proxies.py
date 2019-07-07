import requests
import json
import time
from django.core.cache import cache

#
# 这个我真的不懂要怎么改  还活着的账号密码都写在下面了
#
headers_login ={
    "authority": "www.jufaanli.com",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36"
}
user_password = [
    {
        "user":"17307817096",
        "password":"qmy123456"
    },
    {
        "user":"15750121067",
        "password":"123456789"
    },
    {
        "user":"17354422605",
        "password":"123456789"
    }
]
ssion = requests.session()
user = '18639196180'
password = '12345678'
ip = "58.17.125.215:53281"
def login():

    r = ssion.post(url="https://www.jufaanli.com/home/User/login",headers=headers_login,
                          data={"user":user,"password":password,"is_remember":0},proxies= {"https":ip})

    if r.status_code==200:
        print('成功连接')
        text = json.loads(r.text.replace("", ''), strict=False)
        if text.get("is_to_complete_information")=="hasComplete":
            print('成功登录')
            cache.set("pdf_cookies", r.cookies)
            return True
        else:
            return False

def login_new(user,password):

    r = ssion.post(url="https://www.jufaanli.com/home/User/login",headers=headers_login,
                          data={"user":user,"password":password,"is_remember":0})
    if r.status_code==200:
        print('成功连接')
        text = json.loads(r.text.replace("", ''), strict=False)
        if text.get("is_to_complete_information")=="hasComplete":
            print('成功登录')
            return r.cookies
        else:
            return None
#
# try:
#   if login():
#       f = open("es_list_16.txt","a")
#       # f.write("[")
#       for i in range(1024,1500):
#            res = ssion.post(url="https://www.jufaanli.com/home/search/searchJson",
#                       data={"page":i,"searchTime":int(time.time()),"searchNum":50,
#                                             "nowReason":0,"sortType":"caseWeight","keyword":"案由：敲诈勒索罪",
#                                             "TypeKey":"1:案由：敲诈勒索罪"},proxies= {"https":ip})
#            f.write(res.text)
#            f.write(",")
#            print(i)
#            time.sleep(6)
#
#       f.write("]")
#       f.close()
# except requests.exceptions.ProxyError:
#     print('proxies异常')

