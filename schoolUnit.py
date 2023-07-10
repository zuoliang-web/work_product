import requests
import datetime, time
from lxml import etree
from urllib.parse import urlencode, urljoin
from anti_useragent import UserAgent
import pymysql
from DBUtils.PooledDB import PooledDB
from pymysql.converters import escape_string
import pymongo
import threading

from IdWorker import IdWorker

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
SEL_write_TAB = "journals"
client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(MONGO_USER, MONGO_PASSWD, MONGO_HOST, int(MONGO_PORT)))
db = client[MONGO_DB]
col = db[SEL_write_TAB] 

config = { 
            'host':'192.168.0.120', 
            'port':13709, 
            'user':'elang_user', 
            'password':'elang_backup123', 
            'db':'worldwide', 
            'charset':'utf8',         
            'cursorclass':pymysql.cursors.DictCursor, 
            # 游标设置为字典类型默认值为pymysql.cursors.Cursor。
        } 


class Cmysql:
    
    def __init__(self) -> None:
        
        self.config = { 
            'host':'192.168.0.120', 
            'port':13709, 
            'user':'elang_user', 
            'password':'elang_backup123', 
            'db':'worldwide', 
            'charset':'utf8',         
            'cursorclass':pymysql.cursors.DictCursor, 
            # 游标设置为字典类型默认值为pymysql.cursors.Cursor。
        } 

        self.connection = pymysql.connect(**config)
        # self.cursor = self.connection.cursor()
    



    def _reCon (self): 
            """ MySQLdb.OperationalError异常"""
            # self.con.close() 
            while True:
                try: 
                    self.connection.ping(True)
                    break
                except Exception as e:
                    self.connection  = self.conn()
   
    def select_sql(self, sql):  
        
        self._reCon()
        cursor = self.connection.cursor()   
        try:  
          
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
        except Exception as e:
            data = list()
            print("sql 查询语句错误",e) 
        finally:
            cursor.close()
    
                
        return data
    
    
    def comit_sql(self, sql):
        
        self._reCon() 
        cursor = self.connection.cursor()
        try:
           
            cursor.execute(sql)
            self.connection.commit()  
             
        except Exception as e:
            print("sql 提交语句错误",e) 
            self.connection.rollback()
        finally:
            cursor.close()
           
    
        return True
    
    
    def checkItem(self, sql):
        
        self._reCon() 
        cursor = self.connection.cursor()
        try:   
         
            cursor.execute(sql)
            results = cursor.fetchall()
            if results:
                return None 
        except Exception as e:
            print("sql 查重语句错误",e) 
            self.connection.rollback()
        finally:
            cursor.close()
          
    
        return True


ua = UserAgent()
cmq = Cmysql()
headers = {"User-Agent":""}
def school_unit_spider():
    
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

def article_spider(journal_name, baseid, pcode):
    
    headers = {
        "User-Agent":ua.random
    }

    url = f"https://navi.cnki.net/knavi/journals/{baseid}/yearList?pIdx=0"
    
    while True:
        try:
            response = requests.get(url, headers=headers,proxies=proxies)
            if response.status_code == 200 and response.text:
                xmlobject = etree.HTML(response.text)
            
                yearNumLis = xmlobject.xpath("//div[@class='yearissuepage'][1]/dl")
                if yearNumLis:
                    break
        except Exception as e:
            time.sleep(2)
        
    
    if response.status_code == 200 and response.text:
        xmlobject = etree.HTML(response.text)
        
        yearNumLis = xmlobject.xpath("//div[@class='yearissuepage'][1]/dl")
        ScienceNo = []
        for das in yearNumLis:
            item = dict()
            current_year = das.xpath("./dt/em/text()")[0]
            noLis = das.xpath("./dd/a")
            noLis = {x.xpath("./@value")[0]: x.xpath("./text()")[0] for x in noLis} 
            item["year"] = current_year
            item["code_dict"] = noLis
            ScienceNo.append(item)
        
        
        #  按照年份 - 刊数 进行 抓取
        
        for yIndex,yearEle in enumerate(ScienceNo):    

            print(f" 开始进行，{yearEle['year']}年份抓取------------ ")

            for nIndex, numEle in enumerate(yearEle["code_dict"]):
        
                  
                print(f" 开始进行，{yearEle['year']}年份, 第{yearEle['code_dict'][numEle]}期刊 starting")

                getPageNoInfo(journal_name, numEle, pcode,baseid)
                

def getPageNoInfo(journal_name, year_key, pcode, baseid):
    global headers
    headers["User-Agent"] = ua.random
    data = {
      "yearIssue":year_key,
      "pageIdx": "0",
      "pcode": pcode
    }
    year_headers = {
        "Host":"navi.cnki.net",
        "Origin":"https://navi.cnki.net",
        "Referer":"https://navi.cnki.net/knavi/journals/XDCS/detail?uniplatform=NZKPT&language=chs",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    das = urlencode(data)
    url = f"https://navi.cnki.net/knavi/journals/{baseid}/papers?"
    path = url + das
    
    while True:
        try:
            response = requests.post(path,data=das, headers=year_headers,proxies=proxies)
            break
        except Exception:
            time.sleep(0.52)

    if response.text:
        xmlobject = etree.HTML(response.text)
        
        hrefLis = xmlobject.xpath("//div/dd/span/a")
        
        for obj in hrefLis:
          
            name = obj.xpath("./text()")[0]
            url_path =  obj.xpath("./@href")[0]
            check_sql =  "select id from Modern_Urban_Research where title='%s'" % escape_string(name)
            
            
            if cmq.checkItem(check_sql):
                # 数据存在， 需要更新
                # data = check_title.first()
                # putHistoryArticles(url_path, data)
                postArticles(url_path, journal_name)
                
              
            else:
                # 数据不存在， 需要创建
                continue
            
            time.sleep(1.5)   
                
def postArticles(url, journal_name):
    
    #  response = re(url)
    headers = {
        "Host":"navi.cnki.net",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    while True:
        try:
            response = requests.get(url)
            if response.text:

            # data = Articles()
            
                xmlobj = etree.HTML(response.text)
                        
                title =  xmlobj.xpath("//h1/text()")[0]
                s_id = IdWorker().get_id()
                
                # author
                if xmlobj.xpath("//*[@id='authorpart']/span/a/text()"):
                    authorLis = xmlobj.xpath("//*[@id='authorpart']/span/a")
                    author = ";".join([x.xpath("./text()")[0] for x in authorLis])
                else:
                    author = ""
                
                # company
                if xmlobj.xpath("//div[@class='brief']//h3/a[@class='author']/text()"):
                    companyLis = xmlobj.xpath("//div[@class='brief']//h3/a[@class='author']")
                    company = ";".join([x.xpath("./text()")[0] for x in companyLis])
                else:
                    company = ""  
                
                # pageno
                if xmlobj.xpath("//div[@class='top-tip']/span/a"):
                    noLis = xmlobj.xpath("//div[@class='top-tip']/span/a")
                    pageno = ";".join([x.xpath("./text()")[0] for x in noLis])
                else:
                    pageno = ""  
                
                # 摘要
                if xmlobj.xpath("//*[@id='ChDivSummary']/text()"):
                    summary =  xmlobj.xpath("//*[@id='ChDivSummary']/text()")[0]
                else:
                    summary = "" 

                # 关键词
                if xmlobj.xpath("//p[@class='keywords']/a/text()"):
                    keywords = xmlobj.xpath("//p[@class='keywords']/a/text()")
                    keywords = " ".join([x.strip() for x in keywords])
                else:
                    keywords = ""       

                # 专辑
                if xmlobj.xpath("//span[@class='rowtit' and contains(text(), '专辑：')]/../p/text()"):
                    collection = xmlobj.xpath("//span[@class='rowtit' and contains(text(), '专辑：')]/../p/text()")[0]
                else:
                    collection = ""   
                
                # 专题
                if xmlobj.xpath("//span[@class='rowtit' and contains(text(), '专题：')]/../p/text()"):
                    topic = xmlobj.xpath("//span[@class='rowtit' and contains(text(), '专题：')]/../p/text()")[0]
                else:
                    topic = ""   
                
                # DOI
                if xmlobj.xpath("//span[@class='rowtit' and contains(text(), 'DOI：')]/../p/text()"):
                    DOI = xmlobj.xpath("//span[@class='rowtit' and contains(text(), 'DOI：')]/../p/text()")[0]  
                else:
                    DOI = ""    
                
                # 分类号
                if xmlobj.xpath("//span[@class='rowtit' and contains(text(), '分类号：')]/../p/text()"):
                    type_code = xmlobj.xpath("//span[@class='rowtit' and contains(text(), '分类号：')]/../p/text()")[0]  
                else:
                    type_code = ""   
                    
                
                # 基金资助
                if xmlobj.xpath("//span[@class='rowtit' and contains(text(), '基金资助')]/../p[@class='funds']/a/text()"): 
                    funds = xmlobj.xpath("//span[@class='rowtit' and contains(text(), '基金资助')]/../p[@class='funds']/a")  
                    funds = " ".join([x.xpath("./text()")[0] for x in funds])
                else:
                    funds = ""   
                    
                # 论文大小
                if xmlobj.xpath("//p[@class='total-inform' ]/span[contains(text(), '大小：')]/text()"):
                    size = xmlobj.xpath("//p[@class='total-inform' ]/span[contains(text(), '大小：')]/text()")[0].replace("大小：", "").strip()
                else:
                    size = ""     
                
                # 页码数
                if xmlobj.xpath("//p[@class='total-inform' ]/span[contains(text(), '页数：')]/text()"):
                    pagenum = xmlobj.xpath("//p[@class='total-inform' ]/span[contains(text(), '页数：')]/text()")[0].replace("页数：", "").strip()
                else:
                    pagenum = ""    
                # 下载数
                if xmlobj.xpath("//p[@class='total-inform' ]/span[contains(text(), '下载：')]/text()"):
                    download_num = xmlobj.xpath("//p[@class='total-inform' ]/span[contains(text(), '下载：')]/text()")[0].replace("下载：", "").strip()
                else:
                    download_num = ""   
                create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            
                ins_sql = """
                insert into Modern_Urban_Research(`title`,`author`,`company`,`pageno`,`summary`,`keywords`,`collection`,`topic`,`DOI`,`type_code`,`funds`,`size`,`pagenum`,`download_num`,`create_time`)
                value('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
                """ % (escape_string(title),author,escape_string(company),pageno,escape_string(summary),keywords,escape_string(collection),topic,DOI,type_code,escape_string(funds),size,pagenum,download_num,create_time)
                cmq.comit_sql(ins_sql)
                return True
        except Exception as e:
            postArticles(url, journal_name)
        
        
if __name__ == "__main__":
    
    
    article_spider("现代城市研究", "XDCS", "CJFD,CCJD")

    