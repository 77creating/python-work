"""
    版本:v2
    说明:考虑到每个 函数功能相互之间有影响，不能独立存在，所以打包成了类。
    更新：
        1.get_json_data优化referer传递参数
        2.获取token与数据均使用一套headers

"""
import requests
import json
import pandas as pd
from  urllib.parse import urlencode, quote_plus
class get_wencaiData():
    def __init__(self,*args):
        self.args   =args
        self.params= (
                        ('type','1'),
                        ('preParams',''),
                        ('ts','1'),
                        ('f', '1'),
                        ('qs','result_rewrite'),
                        ('selfsectsn',''),
                        ('querytype','stock'),
                        ('searchfilter',''),
                        ('tid','stockpick'),
                        ('w',list(args)),
                        ('queryarea','')
                    )
        self.dictParams=dict(self.params)
        self.dictParams['w']=','.join(args)
        self.encodeUrlParams=urlencode(self.dictParams,quote_via=quote_plus)
        self.headers={
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'en-US,en;q=0.9,zh;q=0.8',
                        'hexin-v': 'ApwrLLTjK1uE_9-H3qayTjugbbFNFUFcwrxUBXadqHtrOjJnniUQzxLJJIPF',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Referer': 'http://x.10jqka.com.cn/stockpick/search?{}'.format(self.encodeUrlParams),
                        'X-Requested-With': 'XMLHttpRequest',
                        'Connection': 'keep-alive',
                    }


    def get_token_value(self,*args):
        if len(args)==0:return '输入要查询的指标'
        tokenUrl='http://x.10jqka.com.cn/stockpick/load-data'
        try:
            response = requests.get(tokenUrl, headers=self.headers, params=self.dictParams)
            token=json.loads(response.text)['data']['result']['token']
            return token
        except:
            raise TypeError(response.text)
    def get_json_data(self,token,p=1):
        try:
            url='http://x.10jqka.com.cn/stockpick/cache'
            cookies = {
                'sp_search_last_right_status': 'hide',
                'cid': 'f068d2ba77fcca2118f71b2d394febcf1542607353',
                'ComputerID': 'f068d2ba77fcca2118f71b2d394febcf1542607353',
                'guideState': '1',
                'PHPSESSID': 'c9bf450b0dfc2d20caa96215d38d8723',
                'ver_mark': 'c',
                'v': 'ApwrLLTjK1uE_9-H3qayTjugbbFNFUFcwrxUBXadqHtrOjJnniUQzxLJJIPF',
            }

            params = (
                ('token', token),
                ('p', p),
                ('perpage', '70'),
            )
            response = requests.get(url, headers=self.headers, params=self.dictParams, cookies=cookies)
            data=response.json()
            total=data['total']
            return data,total
        except Exception as e:
            return e,data
    def parse_data(self,token,args):

        data,total=self.get_json_data(token=token)#获取第一页数据默认
    #     cols=[x.replace('<br>','-') for x in data['indexID']]
        cols=data['indexID']
        df=pd.DataFrame(columns=cols)
        page=int(total/70)+1 if int(total/70)<total/70  else int(total/70)
        df=pd.DataFrame(data['result'],columns=cols)
        if page==1:return df
        else:
            try:
                for p in range(1,page):
                    i=0#每次获取10次token，如果失败，结束
                    data,total=self.get_json_data(token,p)
                    while i<=10 and isinstance(total,tuple):
                        print('token失效，获取{}次token'.format(i))
                        token=self.get_token_value(args)#获取新的token值
                        data,total=self.get_json_data(token,p)#(KeyError('total'), {'code': 130, 'error': 'token已失效', 'success': False})
                        i +=1
                    dfs=pd.DataFrame(data['result'],columns=cols)
                    df=df.append(dfs)
                    print('已成功获取{}页数据，总共{}页,剩余{}页,token={}'.format(p,page,page-p,token))
                df=df.reset_index()
                return df
            except:
                print('已成功获取{}页数据，总共{}页，剩余{}页,token={}'.format(p,page,page-p,token))
                df=df.reset_index()
                return df

    def get_search_data(self):
        try:
            token=self.get_token_value(self.args)
            df=parse_data(token,self.args)
            df['首次涨停时间'],df['最终涨停时间']=pd.to_datetime(df['首次涨停时间'],unit='ms',utc=1).dt.tz_convert('Asia/Shanghai'),\
                                               pd.to_datetime(df['最终涨停时间'],unit='ms',utc=1).dt.tz_convert('Asia/Shanghai')
            return df
        except:
            return df