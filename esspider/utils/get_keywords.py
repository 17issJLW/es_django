import jieba

# 从其他地方获取  暂时伪造一些
reasons_dict = ['故意杀人罪', '故意伤害罪', '非法拘禁罪']
time_dict = ['2017', '2018', '2019']
stage_dict = ['一审', '二审', '再审']
location_dict = ['北京市','重庆市','天津市','上海市','河北省','山西省','内蒙古自治区','黑龙江省','吉林省','辽宁省','陕西省','甘肃省','青海省','新疆维吾尔自治区','宁夏回族自治区','山东省','河南省','江苏省','浙江省','安徽省','江西省','福建省','台湾省','湖北省','湖南省','广东省','广西壮族自治区','海南省','四川省','云南省','贵州省','西藏自治区']

def get_keywords(s):
    reasons = []
    time = []
    stage = []
    location = []
    jieba.load_userdict('text.txt')
    word_list = jieba.cut(s)
    
    for word in word_list:
        reasons  += filter(lambda item: word in item, reasons_dict)
        time     += filter(lambda item: word in item, time_dict)
        stage    += filter(lambda item: word in item, stage_dict)
        location += filter(lambda item: word in item, location_dict)

    keywords = {
        'reason': list(set(reasons)),
        'time': list(set(time)),
        'stage': list(set(stage)),
        'location': list(set(location))
    }

    return keywords

#测试
# print(get_keywords(s='17故意，二审，天津'))