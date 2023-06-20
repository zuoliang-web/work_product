import requests
import datetime, time
from lxml import etree
from urllib.parse import urlencode, urljoin
from anti_useragent import UserAgent
import pymongo

proxyHost = "ip4.hahado.cn"
proxyPort = "47333"
proxyUser = "196820"
proxyPass = "196820"
proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host" : proxyHost,
    "port" : proxyPort,
    "user" : proxyUser,
    "pass" : proxyPass,
}
proxies = {
    "http"  : proxyMeta,
    "https" : proxyMeta,
} 

MONGO_USER = "root"
MONGO_PASSWD = "abcd1234"
MONGO_HOST = "192.168.0.120"
MONGO_PORT = "27017"
MONGO_DB = "school_data"
SEL_write_TAB = "test_degree"
client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(MONGO_USER, MONGO_PASSWD, MONGO_HOST, int(MONGO_PORT)))
db = client[MONGO_DB]
col = db[SEL_write_TAB] 


def head_info():
    ua = UserAgent()
    base_url = "https://navi.cnki.net/"
    start_url = "https://navi.cnki.net/knavi/degreeunits/searchbaseinfo"
    params = {
            "searchStateJson":{"StateID":"", "Platfrom":"", "QueryTime":"", "Account":"knavi","ClientToken":"","Language":"","CNode":{"PCode":"DEGREE","SMode":"","OperateT":""},"QNode":{"SelectT":"","Select_Fields":"","S_DBCodes":"","QGroup":[],"OrderBy":"RT|","GroupBy":"","Additon":""}},
            "displaymode":"1",
            "pageindex":"1",
            "pagecount":"21",
            "index":"",
            "searchType":"学位授予单位名称",
            "clickName":"",
            "switchdata":"clickTabSearch"
        }
    headers = {
        "Content-Type":'application/x-www-form-urlencoded',
        'Host': 'navi.cnki.net',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'origin':'https://navi.cnki.net',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer':'https://navi.cnki.net/knavi/degreeunits/index?uniplatform=NZKPT&language=chs',
        }
    das = urlencode(params).replace('%27', '%22')
    
    response = requests.post(start_url, data=das, headers=headers, proxies=proxies)
    xmlobj = etree.HTML(response.text)
    current_page = 2
    schoolDict = {}
    while True:
        
        schoolInfo = xmlobj.xpath("//ul[@class='list_tup']/li")    
        
        for item in schoolInfo:  
            name = item.xpath(".//div[@class='detials']/h1/text()")[0]
            href = urljoin(base_url, item.xpath("./a/@href")[0])
            baseid = href.split("baseid=")[-1]
            schoolDict[name] = baseid

        params["switchdata"] = ""
        params["pageindex"] = str(current_page)  
        current_page += 1  
        
        if current_page > 41:
            break
        das = urlencode(params).replace('%27', '%22')
        while True:
            try:
                response = requests.post(start_url, data=das, headers=headers, proxies=proxies)
            
                if response.text != '<script>window.location.href="/knavi/access/verification"</script>' and response.status_code == 200:
                    schoolInfo = xmlobj.xpath("//ul[@class='list_tup']/li")
                    if schoolInfo:
                        break
            except Exception as e:
                time.sleep(0.5)
                print(e)
        xmlobj = etree.HTML(response.text)
        schoolInfo = xmlobj.xpath("//ul[@class='list_tup']/li")

      

    
    for key, value in schoolDict.items():
        
        path = f"https://navi.cnki.net/knavi/degreeunits/{value}/detail?uniplatform=NZKPT"
        # yield scrapy.Request(path,method="GET", headers=headers, meta = {"baseid": value}, callback=self.parse_detail)
        while True:
            try:
                resp = requests.get(path, headers=headers,  proxies=proxies)
                if resp.text != '<script>window.location.href="/knavi/access/verification"</script>' and resp.status_code == 200:
                    time.sleep(0.5)
                    break
            except Exception as e:
                pass
        detail_obj = etree.HTML(resp.text)
        item = dict()
        area = detail_obj.xpath("//p[@class='hostUnit']/span/text()")[0].strip()
        name = detail_obj.xpath("//h3[@class='titbox']/text()")[0].strip()
        artical_counts = detail_obj.xpath("//p[@class='hostUnit']/label[contains(text(),'文献篇数')]/../span/text()")[0].replace("篇", "") if detail_obj.xpath("//p[@class='hostUnit']/label[contains(text(),'文献篇数')]/../span/text()") else ""
        citel_counts = detail_obj.xpath("//p[@class='hostUnit']/label[contains(text(),'总被引次数')]/../span/text()")[0].replace("次", "") if detail_obj.xpath("//p[@class='hostUnit']/label[contains(text(),'总被引次数')]/../span/text()") else ""
        download_counts = detail_obj.xpath("//p[@class='hostUnit']/label[contains(text(),'总下载次数')]/../span/text()")[0].replace("次", "") if  detail_obj.xpath("//p[@class='hostUnit']/label[contains(text(),'总下载次数')]/../span/text()") else ""
        img_path = "https"+detail_obj.xpath("//*[@id='J_journalPic']/img/@src")[0] if detail_obj.xpath("//*[@id='J_journalPic']/img/@src") else ""
        tags = detail_obj.xpath("//h3[@class='titbox']/span/text()")[0] if  detail_obj.xpath("//h3[@class='titbox']/span/text()") else ""
        
        item["area"] = area
        item["name"] = name
        item["artical_counts"] = artical_counts
        item["citel_counts"] = citel_counts
        item["download_counts"] = download_counts
        item["img_path"] = img_path
        item["tags"] = tags
        item["baseid"] =  value
        item["source"] = "CNKI" 
        item["path"] = response.url
        item["create_time"] = datetime.datetime.now()
        
        col.insert_one(item)

head_info()