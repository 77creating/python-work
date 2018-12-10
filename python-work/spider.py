import requests as req
import re
from lxml import etree
def get_com_name(url):
    try:
        header={'user-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        res=req.get(url,headers=header)
        kw=re.findall('http://www.beian.gov.cn/portal/registerSystemInfo\?recordcode=\d+',res.text)
        if len(kw) >0:
            res=req.get(kw[0])
            html=etree.HTML(res.text)
            name=html.xpath('/html/body/div[1]/div[5]/div[3]/div[2]/table/tbody/tr[1]/td[2]')
            Name=etree.tounicode(name[0]).split('>')[1].replace('</td','')
            return Name
    except Exception as e:
        return 
def get_com_name_sojson(url):
    header={'user-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    try:
        urlstr='http://www.sojson.com/api/gongan/'+url
        res=req.get(urlstr,headers=header).json()
        return res['data']['comname']
    except Exception as e:
        try:
            urlstr='http://icp.sojson.com/ga2_'+url+'.html'
            res=req.get(urlstr,headers=header).text
            html=etree.HTML(res)
            name=html.xpath('//*[@id="first"]/li[6]/p')
            Name=etree.tounicode(name[0]).replace('<p>','').replace('</p>','')
            return Name
        except Exception as e:
            return str(e)
def main(url):
    x=get_com_name(url) if get_com_name(url) else get_com_name_sojson(url)
    return x
print(main('iflytek.com'))
