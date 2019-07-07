import json
import jieba
import os
import re
import jieba.analyse
import requests
from urllib.parse import quote



law_brief =[
    {
        "name" : "《中华人民共和国民事诉讼法》",
        "brief": "民事诉讼法",
    },
    {
        "name" : "《中华人民共和国刑事诉讼法》",
        "brief": "刑事诉讼法",
    },
    {
        "name" : "《中华人民共和国刑法》",
        "brief": "刑法",
    }
]

# 调用百度api的
baidu_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?access_token=24.baaa3b46f31dd47773b8974f5a6ac7d9.2592000.1564365738.282335-16651003'

# 上传pdf的url的共同部分
base_url = 'https://esdoc-1255312386.cos.ap-guangzhou.myqcloud.com/'



def open_text(uuid:str,file_name:str,root:str):
    doc = {
        "caseName": "",
        "court": "",
        "caseType": [],
        "caseNumber": "",
        "docType": "",
        "reason": "",
        "content": "",
        "litigant": [],
        "time": "",
        "url": "",
        "lawList": [],
        "stage": [],
        "location": "",
        "lawNameList": []

    }

    f_r = open(file_name,'r',encoding ='utf-8')
    # print(f_r.read())
    str = f_r.read()
    f_r.close()

    jieba.load_userdict("text.txt")
    print('已添加自定义词库')
    # print(jieba.get_FREQ("中华人民共和国民事诉讼法"))

    # 获取正文
    str1 = str.replace('\t\t', "\t")
    # print(str1)
    str1 = re.sub(r'[0-9]{1,2} / [0-9]{1,2}', '', str1)  # 去除页码
    str1 = re.sub(r'', '', str1)  # 去除页码
    str1 = re.sub(r'Powered by TCPDF \(www.tcpdf.org\)', '', str1)  # 去除标记
    str1 = str1.replace('\n\n  ', "###")  # 真新段落
    str1 = str1.replace('\n\n', "&&&")  # 真新段落 末尾审判人姓名后直接换行
    str1 = str1.replace('\n', "")  # 假新段落
    # print(str1)
    str1 = re.sub(r'### {0,}### {0,}', '\n  ', str1)  # 恢复段落（换页的情况）
    str1 = str1.replace("###", "\n  ")  # 恢复段落
    str1 = str1.replace('&&&', "\n")  # 恢复换行
    str1 = re.sub(r'\n{1,} {1,}\n{1,}', '', str1)
    content = str1
    # print(str1)
    # print('------------------------------以上为str1-------------------------------')

    seg_list_1 = jieba.cut(str1,cut_all=True)
    str_1 = "/".join(seg_list_1)
    # print(str_1)


    seg_list_2 = jieba.cut(str1)  # 精准模式
    str_2 = "/".join(seg_list_2)
    # print(str_2)

    # 最后要写一个大的异常处理
    # 文书名 1
    caseName = re.search(r'[^\t|\n]*(?=\n)',str1)
    doc["caseName"] = caseName.group(0)
    # 当事人 2
    litigant = get_litigant(caseName.group(0))
    doc["litigant"] = litigant





    # 时间
    time = re.search(r'[1-2][0-9]{3}-[0-9]{2}-[0-9]{2}', str)
    doc["time"] = time.group(0)
    # 案由

    reason = re.search(r'(?<= )[^ 号]+?(?= (?:一|二|三|再)审| 刑罚变更| 其他| 复核| 再审| 执行 | 非诉执行审查)', str1)
    doc["reason"] = reason.group(0)
    print(reason)
    # stage
    stage = re.search(r'(?<=%s ).+?(?= )'%reason.group(0), str1)
    doc["stage"] = stage.group(0)
    print(stage)

    # 案号
    try:
        caseNumber = re.search(r'(?:（|\()[1-2][0-9]{3}(?:）|\))[^号]*?号', str1)
        doc["caseNumber"] = caseNumber.group(0)
        print(caseNumber)
    except AttributeError:
        try:
            caseNumber = re.search(r'(?<= )《.*?最高人民法院公报》.+?(?= )', str1)
            doc["caseNumber"] = caseNumber.group(0)
            print(caseNumber)
        except AttributeError:
            caseNumber = re.search(r'[^ ]+?(?= %s)'%reason.group(0), str1)
            doc["caseNumber"] = caseNumber.group(0)
            print(caseNumber)

    # url
    url = get_doc_url(caseName.group(0)+'_'+caseNumber.group(0))
    doc["url"] = url

    # 法院
    court = re.search(r'(?<= )[^ 《]+?(人民)*法院', str1)
    court = re.sub(r'行政|[刑民]事','',court.group(0))
    doc["court"] = court
    print(court)
    # 地理位置
    if court == '最高人民法院':
        location = '北京市'
        doc["location"] = location
    else:
        location = re.search(r'.*?(?=((?:高|中|初)级)*(人民)*法院)', court)
        location = re.sub(r'(?:第(?:一|二|三|四|五|六)|铁路运输)', '', location.group(0))
        doc["location"] = location
        print(location)
    # 案件类型
    caseType = []
    caseType_1 = re.search(r'(?:行政|[刑民]事|国家赔偿)', str_1)
    caseType.append(caseType_1.group(0))
    caseType_2 = re.search(r'(?:判决|裁定|决定|调解|通知)', str_1)
    caseType.append(caseType_2.group(0))
    doc["caseType"] = caseType
    print(caseType)
    # 文书类型
    try:
        docType = re.search(r'刑事附带民事..书', caseName.group(0))
        doc["docType"] = docType.group(0)
        print(docType)
    except:
        docType = caseType_1.group(0)+ caseType_2.group(0)+'书'
        doc["docType"] = docType
        print(docType)
    # 全文
    doc["content"] = content
    # lawNameList
    lawNameList = re.findall(r'《中[^》]*?法》', str1)
    temp = re.findall(r'(?:＜|〈)中华人民共和国[^》]*?法(?:＞|〉)', str1)
    print(temp)
    lawNameList_ = []
    for name in temp:
        name_1 = re.sub(r'(?:＜|〈)','《',name)
        name_2 = re.sub(r'(?:＞|〉)','》', name_1)
        lawNameList_.append(name_2)
    lawNameList = lawNameList + lawNameList_
    lawNameList =list(set(lawNameList))
    doc["lawNameList"] = lawNameList
    print(lawNameList)
    # lawList
    lawList = []          #  具体到第几条
    law = []              #  法律（某部）的名称列表
    law_first_part = []   # 进行两次搜索 这是第一次得到的结果
    law_second_part = []
    base_law = re.findall(r'《中[^》]*?法》[^，、及]*?第[^，、及]*?条', str1)
    temp = []
    for i in base_law:
        temp.append(re.sub(r'(?:\（|\().+简称.+?(?:\)|）)', '', i))
    for i in temp:
        law_first_part.append(re.sub(r'(?:\（|\(|\)|）)','',i))
    for i in base_law:
        law_full_name = re.search(r'《[^》]*》',i).group(0)
        law.append(law_full_name)
    temp_str1 = str1
    for i in law:
       for j in  law_brief:
          if j["name"]==i:
             temp_str1 = str1.replace(j["brief"],j["name"])
    temp_2 = re.findall(r'《中[^》]*法》第[^，、]*?条', temp_str1)
    for i in temp_2:
        law_second_part.append(re.sub(r'(?:\（|\(|\)|）)','',i))
    lawList = law_first_part +law_second_part
    lawList = list(set(lawList))
    doc["lawList"] = lawList

    print(doc)

    with open(root+'/'+uuid + '.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(doc))

def get_litigant(text_tilte:str):
    url = baidu_url
    # print(url)
    litigant = []
    post_data = {
        "text":""
    }
    post_data["text"]=text_tilte
    sess = requests.session()
    r =sess.post(url=url,data=json.dumps(post_data),headers={'Content-Type': 'application/json'})
    content = r.text
    if (content):
        # print(content)
        text = json.loads(content)
        print(text)
        for record in text["items"]:
           if record['ne'] == 'PER':
               # print(record['item'])
               litigant.append(record['item'])
    return litigant







def get_list(dirname):
    for root, dirs, files in os.walk(dirname):
        return files

# 通用 返回上传至服务器的pdf的url -》以便写入字典
def get_doc_url(text_tilte:str):
    key_name = text_tilte+'.pdf'
    url = base_url + quote(key_name)
    return url


# 测试
# path ='0f6cc9d559953147420203e1da180e93.txt'
# root ='.'
# uuid ='测试dict'
# # file_name——txt全名  root 写入文件的路径  uuid 写入文件的文件名(可以随便改成别的
# open_text(file_name=path,root=root,uuid=uuid)





# open_text('./txt/0ff129a60b3fb217fd98e0172d5d0f25.txt')

# list_ = get_list(r'C:\Users\Q\PycharmProjects\text\each_txt_14')
# i = 0
#
# root = './each_dict_14'
# count = 0
# # file_name = '009e9b0d8f98ec18c9853325487eb8ef.txt'
# # uuid = re.sub(r'.txt', '', file_name)
# # path = './each_txt_7/'+ file_name
# for file_name in list_:
#     uuid = re.sub(r'.txt', '', file_name)
#     path = './each_txt_14/'+ file_name
#     i = i+1
#     print(i)
#     print(uuid)
#     if os.path.exists(root+uuid+'.txt'):
#         print('存在与' + uuid + '对应的dict')
#     else:
#         print('不存在与' + uuid + '对应的dict')
#         try:
#             open_text(file_name=path,root=root,uuid=uuid)
#         except
# print(count)

def open_text_new(uuid:str,text, root:str):
    doc = {
        "caseName": "",
        "court": "",
        "caseType": [],
        "caseNumber": "",
        "docType": "",
        "reason": "",
        "content": "",
        "litigant": [],
        "time": "",
        "url": "",
        "lawList": [],
        "stage": [],
        "location": "",
        "lawNameList": []

    }
    str = text
    jieba.load_userdict(os.getcwd()+"/esspider/utils/text.txt")
    print('已添加自定义词库')

    # 获取正文
    str1 = str.replace('\t\t', "\t")
    # print(str1)
    str1 = re.sub(r'[0-9]{1,2} / [0-9]{1,2}', '', str1)  # 去除页码
    str1 = re.sub(r'', '', str1)  # 去除页码
    str1 = re.sub(r'Powered by TCPDF \(www.tcpdf.org\)', '', str1)  # 去除标记
    str1 = str1.replace('\n\n  ', "###")  # 真新段落
    str1 = str1.replace('\n\n', "&&&")  # 真新段落 末尾审判人姓名后直接换行
    str1 = str1.replace('\n', "")  # 假新段落
    # print(str1)
    str1 = re.sub(r'### {0,}### {0,}', '\n  ', str1)  # 恢复段落（换页的情况）
    str1 = str1.replace("###", "\n  ")  # 恢复段落
    str1 = str1.replace('&&&', "\n")  # 恢复换行
    str1 = re.sub(r'\n{1,} {1,}\n{1,}', '', str1)
    content = str1
    # print(str1)
    # print('------------------------------以上为str1-------------------------------')

    seg_list_1 = jieba.cut(str1,cut_all=True)
    str_1 = "/".join(seg_list_1)
    # print(str_1)


    seg_list_2 = jieba.cut(str1)  # 精准模式
    str_2 = "/".join(seg_list_2)
    # print(str_2)

    # 最后要写一个大的异常处理
    # 文书名 1
    caseName = re.search(r'[^\t|\n]*(?=\n)',str1)
    doc["caseName"] = caseName.group(0)
    # 当事人 2
    litigant = get_litigant(caseName.group(0))
    doc["litigant"] = litigant





    # 时间
    time = re.search(r'[1-2][0-9]{3}-[0-9]{2}-[0-9]{2}', str)
    doc["time"] = time.group(0)
    # 案由

    reason = re.search(r'(?<= )[^ 号]+?(?= (?:一|二|三|再)审| 刑罚变更| 其他| 复核| 再审| 执行 | 非诉执行审查)', str1)
    doc["reason"] = reason.group(0)
    print(reason)
    # stage
    stage = re.search(r'(?<=%s ).+?(?= )'%reason.group(0), str1)
    doc["stage"] = stage.group(0)
    print(stage)

    # 案号
    try:
        caseNumber = re.search(r'(?:（|\()[1-2][0-9]{3}(?:）|\))[^号]*?号', str1)
        doc["caseNumber"] = caseNumber.group(0)
        print(caseNumber)
    except AttributeError:
        try:
            caseNumber = re.search(r'(?<= )《.*?最高人民法院公报》.+?(?= )', str1)
            doc["caseNumber"] = caseNumber.group(0)
            print(caseNumber)
        except AttributeError:
            caseNumber = re.search(r'[^ ]+?(?= %s)'%reason.group(0), str1)
            doc["caseNumber"] = caseNumber.group(0)
            print(caseNumber)

    # url
    url = get_doc_url(caseName.group(0)+'_'+caseNumber.group(0))
    doc["url"] = url

    # 法院
    court = re.search(r'(?<= )[^ 《]+?(人民)*法院', str1)
    court = re.sub(r'行政|[刑民]事','',court.group(0))
    doc["court"] = court
    print(court)
    # 地理位置
    if court == '最高人民法院':
        location = '北京市'
        doc["location"] = location
    else:
        location = re.search(r'.*?(?=((?:高|中|初)级)*(人民)*法院)', court)
        location = re.sub(r'(?:第(?:一|二|三|四|五|六)|铁路运输)', '', location.group(0))
        doc["location"] = location
        print(location)
    # 案件类型
    caseType = []
    caseType_1 = re.search(r'(?:行政|[刑民]事|国家赔偿)', str_1)
    caseType.append(caseType_1.group(0))
    caseType_2 = re.search(r'(?:判决|裁定|决定|调解|通知)', str_1)
    caseType.append(caseType_2.group(0))
    doc["caseType"] = caseType
    print(caseType)
    # 文书类型
    try:
        docType = re.search(r'刑事附带民事..书', caseName.group(0))
        doc["docType"] = docType.group(0)
        print(docType)
    except:
        docType = caseType_1.group(0)+ caseType_2.group(0)+'书'
        doc["docType"] = docType
        print(docType)
    # 全文
    doc["content"] = content
    # lawNameList
    lawNameList = re.findall(r'《中[^》]*?法》', str1)
    temp = re.findall(r'(?:＜|〈)中华人民共和国[^》]*?法(?:＞|〉)', str1)
    print(temp)
    lawNameList_ = []
    for name in temp:
        name_1 = re.sub(r'(?:＜|〈)','《',name)
        name_2 = re.sub(r'(?:＞|〉)','》', name_1)
        lawNameList_.append(name_2)
    lawNameList = lawNameList + lawNameList_
    lawNameList =list(set(lawNameList))
    doc["lawNameList"] = lawNameList
    print(lawNameList)
    # lawList
    lawList = []          #  具体到第几条
    law = []              #  法律（某部）的名称列表
    law_first_part = []   # 进行两次搜索 这是第一次得到的结果
    law_second_part = []
    base_law = re.findall(r'《中[^》]*?法》[^，、及]*?第[^，、及]*?条', str1)
    temp = []
    for i in base_law:
        temp.append(re.sub(r'(?:\（|\().+简称.+?(?:\)|）)', '', i))
    for i in temp:
        law_first_part.append(re.sub(r'(?:\（|\(|\)|）)','',i))
    for i in base_law:
        law_full_name = re.search(r'《[^》]*》',i).group(0)
        law.append(law_full_name)
    temp_str1 = str1
    for i in law:
       for j in  law_brief:
          if j["name"]==i:
             temp_str1 = str1.replace(j["brief"],j["name"])
    temp_2 = re.findall(r'《中[^》]*法》第[^，、]*?条', temp_str1)
    for i in temp_2:
        law_second_part.append(re.sub(r'(?:\（|\(|\)|）)','',i))
    lawList = law_first_part +law_second_part
    lawList = list(set(lawList))
    doc["lawList"] = lawList

    # print(doc)
    return json.dumps(doc)
    #
    # with open(root+'/'+uuid + '.txt', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(doc))