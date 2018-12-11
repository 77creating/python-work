"""
    版本:v3
    更新：
        1.如果访问失败需要手动获取cookies中的,V值,并将v值替换掉self.cookies['v']即可，下个版本争取拿到这个v值改成自动
        2.token保存在文件中，如果失败则获取新的更新文件
		3.get_json_data增加10次失败的尝试

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
        self.token= open('token.txt','r').read()
        self.dictParams=dict(self.params)
        self.dictParams['w']=','.join(args)
        self.encodeUrlParams=urlencode(self.dictParams,quote_via=quote_plus)
        self.headers=headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'en-US,en;q=0.5',
                                'DNT': '1',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1',
                            }
#         self.headers={
#                         'Accept-Encoding': 'gzip, deflate',
#                         'Accept-Language': 'en-US,en;q=0.9,zh;q=0.8',
#                         'hexin-v': 'ApwrLLTjK1uE_9-H3qayTjugbbFNFUFcwrxUBXadqHtrOjJnniUQzxLJJIPF',
#                         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
#                         'Accept': 'application/json, text/javascript, */*; q=0.01',
#                         'Referer': 'http://x.10jqka.com.cn/stockpick/search?{}'.format(self.encodeUrlParams),
#                         'X-Requested-With': 'XMLHttpRequest',
#                         'Connection': 'keep-alive',
#                     }
        self.cookies= {
                        'cid': 'f7f4157eb5fac263c5b24f8f6419d1dc1544424078',
                        'ComputerID': 'f7f4157eb5fac263c5b24f8f6419d1dc1544424078',
                        'guideState': '1',
                        'ver_mark': 'b',
                        'Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1': '1544424285,1544424558',
                        'Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1': '1544424558',
                        'PHPSESSID': '2afd8e31670232143ec84c9842638d71',
                        'v': 'AoXMFWmYdQuwL1FXsxRb1RrflMq8QjgLg_cdAofpQdDJPqu8T5JJpBNGLfcU',  
        }


    def get_token_value(self,*args):
        if len(args)==0:return '输入要查询的指标'
        tokenUrl='http://x.10jqka.com.cn/stockpick/load-data'
        
        try:
            response = requests.get(tokenUrl, headers=self.headers, params=self.dictParams,cookies=self.cookies)
            self.token=json.loads(response.text)['data']['result']['token']
            with open('token.txt','w') as f:
                f.write(self.token)
            return self.token
        except:
            raise TypeError(response.text,response.url)
    def get_json_data(self,p=1):
        i=0
        while i<=10:
            url='http://x.10jqka.com.cn/stockpick/cache'
            i +=1
            params = (
                ('token', self.token),
                ('p', p),
                ('perpage', '70'),
                ('showType', '["","","onTable","onTable","onTable", \
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable","onTable",\
                             "onTable","onTable","onTable"]')

            )
            response = requests.get(url, headers=self.headers, params=self.dictParams, cookies=self.cookies)
            try:
                data=response.json()
                
                if isinstance(data,dict):
                    if 'code' in data:
                        print('token失效,更新token')
                        self.token=self.get_token_value(args)#获取新的token值
                        continue
                    else:
                        total=data['total']
                        return data,total
            except Exception:
                print('数据获取失败，尝试第{}次'.format(i),response.text,self.token)
#                 self.cookies['PHPSESSID']='2afd8e31670232143ec84c9842638d71'
                self.cookies['v']='AgBJGsQTSMwOITTIa3OWMn_00YXRieDHhmU4AXqSzJuu9a4zIpm049Z9CPPJ'
                continue
                #(KeyError('total'), {'code': 130, 'error': 'token已失效', 'success': False})
  
    def parse_data(self,token,args):
        data,total=self.get_json_data()#获取第一页数据默认
    #     cols=[x.replace('<br>','-') for x in data['indexID']]
        cols=data['indexID']
        df=pd.DataFrame(columns=cols)
        page=int(total/70)+1 if int(total/70)<total/70  else int(total/70)
        df=pd.DataFrame(data['result'],columns=cols)
        if page==1:return df
        else:
            try:
                for p in range(2,page):
                    data,total=self.get_json_data(p)
                    dfs=pd.DataFrame(data['result'],columns=cols)
                    df=df.append(dfs)
                    print('已成功获取{}页数据，总共{}页,剩余{}页,token={}'.format(p,page,page-p,token))
                df=df.reset_index()
                return df
            except Exception as e:
                print('已成功获取{}页数据，总共{}页，剩余{}页,token={},错误:{}'.format(p,page,page-p,token,e))
                df=df.reset_index()
                return df

    def get_search_data(self):
        
        try:
            #读取token由立即获取替换成文件保存的形式
#             token=self.get_token_value(self.args)
            df=self.parse_data(self.token,self.args)
            df['首次涨停时间'],df['最终涨停时间']=pd.to_datetime(df['首次涨停时间'],unit='ms',utc=1).dt.tz_convert('Asia/Shanghai'),\
                                               pd.to_datetime(df['最终涨停时间'],unit='ms',utc=1).dt.tz_convert('Asia/Shanghai')
            return df
        except:
            return df
    def getListData(self,df,code):
#         codeCols=['涨停时间','涨停打开时间','持续时间','首次封单量','占实际流通比','占成交量比','最高封单量','占实际流通比','占成交量比']
        if '涨停明细数据' in df.columns:
            dataJson=df[df['_stk-code_']==code]['涨停明细数据'].tolist()
            df=pd.DataFrame(dataJson[0])
            df['time'],df['updatedTime'],df['openTime']=pd.to_datetime(df['time'],unit='ms',utc=1).dt.tz_convert('Asia/Shanghai'),\
                                         pd.to_datetime(df['updatedTime'],unit='ms',utc=1).dt.tz_convert('Asia/Shanghai'), \
                                         pd.to_datetime(df['openTime'],unit='ms',utc=1).dt.tz_convert('Asia/Shanghai')  
            df.duration=df.duration/(1000*60)
#             df.columns=codeCols
            return df
        else:
            raise ValueError('无[涨停明细]数据字段')
            return 
        