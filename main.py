# coding=utf-8
# Filename:hello_world.py

import logging
import time
import werobot
import requests
import json
from werobot.replies import ArticlesReply, Article,ImageReply, SuccessReply
from lxml import etree
from imageReco import ImageReco
from translator_multiple import Trans
import sys
from gevent import monkey
import re
import random
from TextRevi import TextReview
monkey.patch_all()

reload(sys)
sys.setdefaultencoding('utf8')

formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
# logfile for improving ability
filenameForUserInput = "./log/"+time.strftime("%Y%m%d_%H%M%S", time.localtime()) +"_UserInput.log"
# collect result
filenameForCollectData = "./log/"+time.strftime("%Y%m%d_%H%M%S", time.localtime()) +"_collectdata.log"

# setup logger
'''
NOTSET（0）、DEBUG（10）、INFO（20）、WARNING（30）、ERROR（40）、CRITICAL（50）
'''
def setup_logger(name, log_file, level=logging.DEBUG):
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

log_user_input = setup_logger('log_user_input', filenameForUserInput)
log_collect_data = setup_logger('log_collect_data', filenameForCollectData)

aImg=ImageReco()
aTran=Trans()
TR=TextReview()

C2E={}

C2E['有害垃圾']='harmful-waste'
C2E['可回收物']='recyclable'
C2E['干垃圾']='residual_waste'
C2E['湿垃圾']='household_food_waste'

E2C = {}
E2C['harmful-waste'] = '有害垃圾'
E2C['recyclable'] = '可回收物'
E2C['residual_waste'] = '干垃圾'
E2C['household_food_waste'] = '湿垃圾'


robot = werobot.WeRoBot(token = 'sapb1')

'''
#test
robot.config["APP_ID"] = "wx40fe985b752f7cf5"
robot.config["APP_SECRET"] ="2b6144472e3307043d3d79b05ea3cb30"

'''
#formal
robot.config["APP_ID"] = "wx3a3a712bb0ef657e"
robot.config["APP_SECRET"] ="420cbcc9e9a99fac7d172b3c34c1009b"


client = robot.client
media_id_hw=client.upload_permanent_media("image",open(r"picture/harmful-waste.jpg","rb"))["media_id"]
media_id_hfw=client.upload_permanent_media("image",open(r"picture/household_food_waste.jpg","rb"))["media_id"]
media_id_I=client.upload_permanent_media("image",open(r"picture/Introduction.jpg","rb"))["media_id"]
media_id_recy=client.upload_permanent_media("image",open(r"picture/recyclable.jpg","rb"))["media_id"]
media_id_resi=client.upload_permanent_media("image",open(r"picture/residual_waste.jpg","rb"))["media_id"]

Reply2Picture={}
Reply2Picture['harmful-waste']=media_id_hw
Reply2Picture['household_food_waste']=media_id_hfw
Reply2Picture['introduction']=media_id_I
Reply2Picture['recyclable']=media_id_recy
Reply2Picture['residual_waste']=media_id_resi
Reply2Picture['greeting']='您好，我是SAP垃圾分类智能助手，是基于SAP Conversation AI开发的聊天机器人。目前我还是一个测试版本，返回结果仅供参考，如果有误请依照上海市最新标准, 如果您发现任何问题请联系邮箱Keguo.Zhou@sap.com或微信zhoukeguo。'+ '\n' \
            +'请输入要查询分类的垃圾。'
Reply2Picture['famous_person']='此人大名鼎鼎，可不是什么垃圾哦[嘿哈]'
reply_none = '你查询的可能是外星物种😱，是除了干垃圾，湿垃圾，有害垃圾和可回收垃圾以外的神秘垃圾，隐藏着巨大的宝藏🎁\n分类建议：自己看着办[机智]\n您也可以输入 + 名称 种类 添加到我的语料库哦[耶]'

def getHtml(webpage):
    t=etree.HTML(webpage)
    Info = []
    Info=t.xpath("//div[@class='info']")
    if( not Info or Info==[]):
        print('sap1')
        return 0
    reply=t.xpath("//div[@class='info']/p/span")
    #print(reply[0].text)
    res = reply[0].text.decode('utf-8')
    print(res)
    if res == '有害垃圾' :
        print('shanghai')
        return C2E['有害垃圾']
    elif res == '可回收物' :
        print('shanghai')
        return C2E['可回收物']
    elif res == '湿垃圾' :
        print('shanghai')
        return C2E['湿垃圾']
    elif res == '干垃圾' :
        print('shanghai')
        return C2E['干垃圾']
    else:
        print('sap2')
        return 0


def GetAnswer(problem,message):
    origin = 'Shanghai'
    r_sh=requests.post('http://trash.lhsr.cn/sites/feiguan/trashTypes_2/TrashQuery_h5.aspx?kw='+problem)
    if(r_sh.status_code==200): #未考虑不是中文的情况
        reply=getHtml(r_sh.text)
    else:
        print('status_code:' + str(r_sh.status_code))
    if(reply==0):
        origin = 'sap'
        payload = {'text':problem, 'language': 'zh'}
        headers = {'Authorization': 'Token 2ddf07e6a963d970354cd553f2a3c425','content-type': 'application/json'}
        r_sap = requests.post("https://api.cai.tools.sap/v2/request", data=json.dumps(payload), headers = headers)
        #print(r.text)
        try:
            intents__=json.loads(r_sap.text)['results']['intents']
        except TypeError:
            print('TypeError Happens:')
            print(json.loads(r_sap.text)['results'])
        if(intents__ == []):
            log_collect_data.info('%s %s %s none %s' %(message.source, problem, message.type, origin))
            return reply_none
        else:
            reply=intents__[0]['slug']

    if(reply=='greeting' or reply=='famous_person' ):
        return Reply2Picture[reply]
    # log record
    log_collect_data.info('%s %s %s %s %s' %(message.source, problem, message.type, reply, origin))
    return ImageReply(message=message,media_id=Reply2Picture[reply])


@robot.filter('测试')
def response(message):
    reply = SuccessReply(message = message)
    #reply = 'success'
    return reply

@robot.filter("你","你呢")
def response(message):
    rep=random.randint(1,3)
    r_message=""
    if rep==1:
        r_message="_(´ཀ`」 ∠)_为什么要扔我，嘤嘤嘤，嘤嘤嘤，嘤嘤嘤嘤嘤"
    elif rep==2:
        r_message="[快哭了]"
    else:
        r_message="系统提醒：您的好友{SAP垃圾分类助手}受到1万点暴击，回复1进行治疗"
    return r_message


@robot.filter("前男友", "前女友","渣男")
def response(message):
    rep=random.randint(1,3)
    r_message=""
    if rep==1:
        r_message="SAP垃圾分类助手不想评价"
    elif rep==2:
        r_message="SAP智能垃圾分类助手表示同情"
    else:
        return ReplyClassification(message)
    return r_message

@robot.filter("熊孩子")
def response(message):
    rep=random.randint(1,3)
    r_message=""
    if rep==1:
        r_message="集齐七个召唤神龙吧"
    elif rep==2:
        r_message="可与熊家长打包投放，类型尚不明确"
    else:
        r_message="SAP智能垃圾分类助手表示同情"
    return r_message

@robot.filter("谢谢","感谢",re.compile(".*?Thank.*?",re.I))
def response(message):
    rep=random.randint(1,4)
    r_message=""
    if rep==1:
        r_message="客气客气"
    elif rep==2:
        r_message="不用谢"
    elif rep==3:
        r_message="很高兴为您服务"
    else:
        r_message="(/ω＼)"
    return r_message

@robot.filter("再见","拜拜","88",re.compile(".*?BYE.*?",re.I))
def response(message):
    return "Bye~~"


@robot.filter("男友","女友","男朋友","女朋友","老公","老婆")
def response(message):
    rep=random.randint(1,5)
    r_message=""
    if rep==1:
        r_message="您的好友{单身的SAP垃圾分类助手}已下线......"
    elif rep==2:
        r_message="您不需要的话可以送给我么，或者可以上交给国家"
    elif rep==3:
        r_message="系统提醒：您的好友{单身狗}受到1万点暴击，回复1进行治疗"
    elif rep==4:
        r_message="You Need To Calm Down"
    else:
        r_message="......."
    return r_message

@robot.filter(re.compile(".*?Nice to meet you.*?",re.I), "你好",re.compile("hello",re.I),re.compile("hi",re.I),"1","你好呀","你好啊")
def response(message):
    rep=random.randint(1,5)
    r_message=""
    if rep==1:
        r_message="请问您有什么垃圾需要我分类呢？"
    elif rep==2:
        r_message="让我瞧瞧你有啥垃圾[奸笑]"
    elif rep==3:
        r_message="垃圾来了[调皮]垃圾来了[调皮]\n侬zi撒喇希？你是什么垃圾？[奸笑][奸笑]"
    elif rep==4:
        r_message="SAP Waste Classification Assistant at your service, Sir!"
    else:
        r_message="[捂脸][捂脸]客气客气,有什么可以帮助您的吗？"
    return r_message

str_acc = '.*?珍珠奶茶.*?'.decode('utf-8')# for Chinese characters use UTF-8
@robot.filter(re.compile(str_acc,re.I),re.compile(".*?奶茶.*?".decode('utf-8')))
def response(message):
    r_message = '麻烦您先把它喝完😉。喝不完时请将奶茶倒入水槽。' + '\n' + '奶茶杯身与杯盖都是干垃圾，但珍珠是湿垃圾。'
    return r_message

@robot.filter("咖啡", "饮料", "果汁", "雪碧", "可乐", "橙汁", "豆浆", "矿泉水", "牛奶")
def response(message):
    r_message = '纯流质的食物垃圾，比如奶茶咖啡牛奶果汁矿泉水等饮料应该直接倒入下水口，容器按垃圾类型放入干垃圾或者可回收垃圾筒。（仅供参考，具体分类要求以属地管理部门为准）'
    return r_message

str_acc = '.*?(汤|矿泉水|汁)$'.decode('utf-8')
@robot.filter(re.compile(str_acc,re.I))
def response(message):
    r_message = '纯流质的食物垃圾，比如奶茶咖啡牛奶果汁矿泉水等饮料应该直接倒入下水口，容器按垃圾类型放入干垃圾或者可回收垃圾筒。（仅供参考，具体分类要求以属地管理部门为准）'
    return r_message


@robot.filter("水")
def response(message):
    r_message = '纯流质的食物垃圾，比如奶茶咖啡牛奶果汁矿泉水等饮料应该直接倒入下水口，容器按垃圾类型放入干垃圾或者可回收垃圾筒。（仅供参考，具体分类要求以属地管理部门为准）'
    return r_message


str_acc = '.*?(SAP|sap).*?'.decode('utf-8')
@robot.filter(re.compile(str_acc,re.I))
def response(message):
    r_message = '亲爱的，我想和你们一起做好垃圾分类，让世界运转更卓越，让人们生活更美好~'
    return r_message

str_acc = '.*?龙虾.*?'.decode('utf-8')
@robot.filter(re.compile(str_acc,re.I))
def response(message):
    r_message = '无论是一整只龙虾，还是龙虾肉，龙虾壳以及龙虾黄。它们都是湿垃圾。😉'
    return r_message

str_shit1 = '.*?屎.*?'.decode('utf-8')
str_shit2 = '.*?粪.*?'.decode('utf-8')
str_shit3 = '.*?粑.*?'.decode('utf-8')
str_shit4 = '.*?大便.*?'.decode('utf-8')

@robot.filter(re.compile(str_shit1,re.I), re.compile(str_shit2,re.I), re.compile(str_shit3,re.I), re.compile(str_shit4,re.I), "小便", "大小便", "便便","尿液", "shit","翔")
def response(message):
    r_message = '大小便，动物粪便，猫屎，狗屎粑粑不属于干垃圾，湿垃圾，有害垃圾和可回收垃圾的任何一种，请大家倒入家中马桶，冲掉。（仅供参考，具体分类要求以属地管理部门为准）'
    return r_message

# let user help to improve the ability
@robot.filter(re.compile("^\+",re.I))
def response(message):
    rep=random.randint(1,3)
    r_message=""
    if rep==1:
        r_message="感谢您帮助我增加知识，让我们共同打造最全的垃圾名词词典。"
    elif rep==2:
        r_message="收到，小助手会努力学习哒!😊"
    else:
        r_message="朝闻道夕可……分垃圾矣😊"
    log_user_input.info('%s %s' %(message.source, message.content))
    return r_message

# if users say it is wrong
@robot.filter(re.compile("wrong",re.I),"错误",re.compile(".*?错了.*?".decode('utf-8')),"不正确","错","不对",re.compile(".*?错啦.*?".decode('utf-8')),"不准确")
def response(message):
    rep=random.randint(1,3)
    r_message=""
    if rep==1:
        r_message="咦？[疑问]那您教教我吗？\n输入+垃圾名词 垃圾类型就能上传垃圾词条补充我的语料库[机智]，比如+电池 有害垃圾"
    elif rep==2:
        r_message="我知道错了[委屈]你能教教我吗？\n输入+垃圾名词 垃圾类型就能上传垃圾词条补充我的语料库[耶]，比如+电池 有害垃圾"
    else:
        r_message="[皱眉]抱歉抱歉，那您能教教我吗？\n输入+垃圾名词 垃圾类型就能上传垃圾词条补充我的语料库[机智]，比如+电池 有害垃圾"
    #log_user_input.info('%s %s' %(message.source, message.content))
    return r_message

#
@robot.filter("太牛了","不错",re.compile("good",re.I),re.compile(".*?真棒.*?".decode('utf-8')),re.compile(".*?厉害.*?".decode('utf-8')),re.compile(".*?你太棒.*?".decode('utf-8')))
def response(message):
    rep=random.randint(1,3)
    r_message=""
    if rep==1:
        r_message="(/ω＼)"
    elif rep==2:
        r_message="谢谢您，我会继续努力的！！[耶]"
    else:
        r_message="[跳跳][跳跳][跳跳][转圈][转圈][转圈]"
    #log_user_input.info('%s %s' %(message.source, message.content))
    return r_message

@robot.filter("？","?")
def response(message):
    return "!"

@robot.filter("奥特曼","咸蛋超人")
def response(message):
    return "您说的是迪迦还是泰罗呢？不过他们都不是垃圾哦[机智]"

# @robot.handler
@robot.text
def ReplyClassification(message):
    raw_problem=message.content
    #aTran=Trans()
    problem=aTran.detect_and_trans(raw_problem)
    print(problem)
    SensitiveWord=TR.recognize(problem)
    if(SensitiveWord): #SensitiveWord
        return '''抱歉，您输入的内容查询不到信息，请重新输入[委屈][委屈][委屈]'''
    else:
        return GetAnswer(problem,message)


@robot.voice
def VoiceReplyClassification(message):
    problem=message.recognition
    problem=problem[:-1]
    print('2:')
    print(problem)
    SensitiveWord=TR.recognize(problem)
    if(SensitiveWord): #SensitiveWord
        return '''抱歉，您输入的内容查询不到信息，请重新输入[委屈][委屈][委屈]'''
    else:
        return GetAnswer(problem,message)


@robot.image
def PictureReplyClassification(message):
    #a=ImageReco()
    begin = time.time()
    url_img=message.img
    #print('url:')
    #print(url_img)

    begin_time=time.time()
    image=aImg.getImage(url_img)
    end_time=time.time()
    print("get image"+str(end_time-begin_time))

    print("compressed length:"+str(len(image)))

    begin_time=time.time()
    problem_list=aImg.recognize(image)
    end_time=time.time()
    print("rec image"+str(end_time-begin_time))
    problem_count=len(problem_list)

    print(problem_list)
    end = time.time()
    time1 = ""
    time1 = str(end - begin)
    print("the program has run " + time1 +'s')
    if((end - begin) > 3.5):
	    return SuccessReply(message = message)
    else:
        return GetAnswerImg(problem_list,message)


@robot.subscribe
def subscribe(message):
    return '''Hello World!
And nice to meet you.
:）
'''

def GetAnswerImg(problem,message):
    origin = 'Shanghai'
    print problem
    res0 = problem[0][0]
    score0 = int(problem[0][1]*100)
    res1 = problem[1][0]
    score1 = int(problem[1][1]*100)
    res2 = problem[2][0]
    score2 = int(problem[2][1]*100)


    #response = '经过我的火眼金睛🕶，照片里的垃圾很有可能是' + res0 + '，或者' + res1 + '，或者' + res2 + '。'
    response_1 = '经过我的火眼金睛🕶，照片里的垃圾很有可能是' + res0 + '。'
    response_2 = '我还不太确定照片里垃圾的类型😅。它可能是:'
    response_none = '你查询的可能是外星物种😱，是除了干垃圾，湿垃圾，有害垃圾和可回收垃圾以外的神秘垃圾。它可能是：'

    SensitiveWord=TR.recognize(res0)
    if(SensitiveWord): #SensitiveWord
        return '''抱歉，您输入的内容查询不到信息，请重新输入[委屈][委屈][委屈]'''

    r_sh=requests.post('http://trash.lhsr.cn/sites/feiguan/trashTypes_2/TrashQuery_h5.aspx?kw='+res0)
    if(r_sh.status_code==200): #未考虑不是中文的情况
        reply=getHtml(r_sh.text)
    else:
        print('status_code:' + str(r_sh.status_code))
    if(reply==0):
        origin = 'sap'
        payload = {'text':res0, 'language': 'zh'}
        headers = {'Authorization': 'Token d67162ab7c89ad345f1359c9822e75ee','content-type': 'application/json'}
        r_sap = requests.post("https://api.cai.tools.sap/v2/request", data=json.dumps(payload), headers = headers)
        #print(r.text)
        try:
            intents__=json.loads(r_sap.text)['results']['intents']
        except TypeError:
            print('TypeError Happens:')
            print(json.loads(r_sap.text)['results'])
        if(intents__ == []):
            # log record
            log_collect_data.info('%s %s %s none %s' %(message.source, problem, message.type, origin))
            response_none = response_none + '\n' + res0 + '  ' + str(score0)+'%' + '\n' + res1 + '  ' + str(score1)+'%' + '\n' + res2 + '  ' + str(score2)+'%' + '。' + '\n' + '我暂时还不知道怎么分类，请让我再多学习几天。[捂脸]'
            return response_none
        else:
            reply=intents__[0]['slug']
            # log record
            log_collect_data.info('%s %s %s %s %s' %(message.source, problem[0][0], message.type, reply, origin))

    if(reply=='greeting' or reply=='famous_person' ):
        return Reply2Picture[reply]
    if(problem[0][1] > 0.8):
        response = response_1  +"\n"+ res0 + '是' + E2C[reply] + '。'
        log_collect_data.info('%s %s %s %s %s' %(message.source, problem[0][0], message.type, reply, origin))
    else:
        response = response_2 + '\n' + res0 + '  ' + str(score0) +'%'+ '\n' + res1 + '  ' + str(score1) +'%'+ '\n' + res2 + '  ' + str(score2)+'%' + '。'
        response = response + '\n' + '其中，' + res0 + '是' + E2C[reply] + '。'
    #return ImageReply(message=message,media_id=Reply2Picture[reply])
    return response

# lisetn at 0.0.0.0:80
robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 80
robot.run(server="gevent")
#robot.run()
