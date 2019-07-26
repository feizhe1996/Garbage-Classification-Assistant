# -*- coding: utf-8 -*-
from googletrans import Translator


class Trans():
    def __init__(self):
        self.trans=Translator(service_urls=['translate.google.cn'])

    def detect_and_trans(self,str):
        language=''
        try:
            language=self.detect(str)
        except UnicodeDecodeError:
            language='ch'

        if(language=='en'):
            #print('English')
            return self.EN2CH(str)
        else:
            return str

    def detect(self,str):
        return self.trans.detect(str).lang

    def EN2CH(self,str):
        return self.trans.translate(str,dest='zh-CN').text


'''
print('张')
a=Trans()
while True:
    #inn=b'苹果'
    try:
        inn=input('input:') #input需要加引号 raw_input不用加引号但是py3会报错
    except:
        print("input needs ''")
        continue
    outt=a.detect_and_trans(inn) #.encode("utf-8") #不能加
    print(outt)
'''


'''

def CH2EN(str):
    translator=Translator(service_urls=['translate.google.cn'])
    return translator.translate(str).text

def EN2CH(str):
    translator=Translator(service_urls=['translate.google.cn'])
    #print(translator.translate(str,dest='zh-CN').text)
    return translator.translate(str,dest='zh-CN').text

def detect(str):
    translator = Translator()
    language=translator.detect(str).lang
    print(f'language: {language}')
    return language

detect('aaa')

'''
