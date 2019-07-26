# -*- coding: utf-8 -*-
from aip import AipImageCensor

APP_ID = '16818813'
API_KEY = '95XZ7r8WGf8yOIHBfvWrkokB'
SECRET_KEY = 'Ef7OIH0VO8OUjtvZgA2VN7eGZ28mEwOi'


class TextReview():
        def __init__(self):
                self.client=AipImageCensor(APP_ID, API_KEY, SECRET_KEY)

        def recognize(self,text):
                ans=self.client.antiSpam(text)
                if('error_msg' in ans.keys()):
                    print(ans['error_msg'])
                    return 0
                ans=ans['result']
                if(ans['reject']==[] and ans['review']==[]): #pass
                    return 0
                return 1
                '''
                if(ans['reject']):
                    return ans['reject'][0]['label']
                else:
                    return ans['review'][0]['label']
                '''
