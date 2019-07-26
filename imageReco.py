# -*- coding: utf-8 -*-
from aip import AipImageClassify
import requests
from PIL import Image
import StringIO
import time

ID='16694077'
AK='RAZx3FONp7SgfbG8nMdALkk4'
SK='VnAo2BgxD6afaXkddpGnGDxkZzvWIRto'

MAX_LEN=100000
REC_SCORE=0.0

class ImageReco():
        def __init__(self):
                self.client=AipImageClassify(ID, AK, SK)
                #self.client.setConnectionTimeoutInMillis(5000)
                #self.client.setSocketTimeoutInMillis(5000)

        '''
        with open(fpath,'rb') as fp:
        return fp.read()
        '''
        def getImage(self,fpath):
                begin=time.time()
                r=requests.get(fpath).content
                end=time.time()
                print("request time: "+str(end-begin))
                while(len(r)>=MAX_LEN):
                        image=Image.open(StringIO.StringIO(r))
                        w,h=image.size
                        image=image.resize((int(2*w/3),int(2*h/3)),Image.ANTIALIAS).convert("L")
                        f=StringIO.StringIO()
                        image.save(f,"JPEG")
                        r=f.getvalue()
                return r
                #print(r.content)
                #return r.content
                '''
                with open(fpath,'rb') as fp:
                        return fp.read()
                '''

        def recognize(self,image):
                begin=time.time()
                result=self.client.advancedGeneral(image)
                end=time.time()
                print("baidu-api :"+str(end-begin))
                keyword_list=[]
                score=0
                result_num=0
                #print(result)
                try:
                        for item in result['result']:
                                print item['keyword'],
                                print(item['score'])

                        result_num=int(result['result_num'])
                        keyword=result['result'][0]['keyword']
                        score= float(result['result'][0]['score'])
                except KeyError:
                        print('KeyError')
                        print(result)
                        return keyword_list
                except BaseException:
                        print('OtherError')
                        print(result)
                        return keyword_list

                #if(score>REC_SCORE):
                        #return [(keyword,score)]
                for item in result['result']:
                        keyword_list.append((item['keyword'],item['score']))
                #print keyword_list
                return keyword_list

'''
a=ImageReco()
image=a.getImage(r'http://mmbiz.qpic.cn/mmbiz_jpg/r9KdW3ZiaqfBONQwbVdEcTgmJtz6RYUPaOtiaSYHdOutfVnEGWu8vNVwgRF8NFLYqNm0apxH9kmd7nUNAXRHUZSg/0')
print(a.recognize(image)[0][1])
'''

'''
client = AipImageClassify(ID, AK, SK)


def getImage(fpath):
    with open(fpath,'rb') as fp:
        return fp.read()

#fpath=input('input file path')
fpath=r'C:\Users\i511508\Documents\workspace\WasteSorting\testImage\timg.jfif'
image=getImage(fpath)

result=client.advancedGeneral(image)
print(result['result'][0]['keyword'])
print(result)
#.encode("utf-8"))
'''
