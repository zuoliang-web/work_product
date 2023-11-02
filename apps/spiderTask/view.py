import time, datetime
import re
from apps.utils.baseRequest import CRequest
from urllib.parse import urlencode, urljoin, quote
from lxml import etree
from apps.dbutils.CMongo import Cmongo

from flask import current_app
from ..utils.commFunc import CAopceptor
from ..dbutils.Ckafka import CKafkaProducer, CKafkaConsumer


def pressUnit():
    crq = CRequest()
    cm = Cmongo()
    
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
    
    response = crq.post(start_url, data=das, headers=headers)
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
                response = crq.post(start_url, data=das, headers=headers)
            
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
                resp = crq.get(path, headers=headers)
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
        degree_type = detail_obj.xpath("//*[@id='J_journalPic']/div[@class='radio']/a/@value")[0]
        pcode =  detail_obj.xpath("//*[@id='pCode']/@value")[0]
        
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
        item["degree_type"] = degree_type
        item["pcode"] = pcode
        
        
        cm.schoolUnitInsert(item)

def retrySid(crq, url, headers):
    resp = crq.get(url, headers=headers)
    response = etree.HTML(resp)
    
    sid = response.xpath("//h1[@class='refirstcol']/a[@title='全部文献']/@id")[0]
    return sid

def pressPaper():
    
    start_url = "https://navi.cnki.net/knavi/degreeunits/subjects?"
    crq = CRequest()
    cm = Cmongo()
    Kproducer = CKafkaProducer()
    Kproducer.connect()
    skip = 32

    results = cm.schoolUnitFind()
    if results:
        for index, data in enumerate(results):
            current = 1
            
            if index < skip:
                continue
            baseid = data["baseid"]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Host":"navi.cnki.net",
                "Referer":"https://navi.cnki.net/knavi/degreeunits/GBHUU/detail?uniplatform=NZKPT", 
                }
            params = {
                "baseId":baseid,
                "scope":"DEGREE"
            }
            das = urlencode(params)
            current_app.logger.info(f'开始抓取  学校名称：{data["name"]}  第{index}个')
            
            resp = crq.get(start_url + das, headers=headers)
            response = etree.HTML(resp)
            
            sid = response.xpath("//h1[@class='refirstcol']/a[@title='全部文献']/@id")[0]
            
            url = f"https://navi.cnki.net/knavi/degreeunits/{sid}/articles"
            subject_params = {
                "pcode":data["pcode"],
                "baseId": data["baseid"],
                "orderBy": "RT|DESC",
                "scope": quote(data["degree_type"]),
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Host":"navi.cnki.net",
                "Referer":f"https://navi.cnki.net/knavi/degreeunits/{data['baseid']}/detail?uniplatform=NZKPT", 
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                }
            subject_params =  urlencode(subject_params).replace('%27', '%22')
            
            while True: 
                listResponse = crq.post(url, headers=headers, data=subject_params)
                if not listResponse:
                    sid = retrySid(crq, start_url + das, headers=headers)
                    url = f"https://navi.cnki.net/knavi/degreeunits/{sid}/articles"
                else:
                    break
            listResp = etree.HTML(listResponse)
            
            articles_infos = dict()
            total = listResp.xpath("//*[@id='pageCount']/@value")[0]
            if total:
                total = int(total)
                
                infos = listResp.xpath("//div[@class='searchresult-list']//table/tbody/tr")
                for info in infos:
                    item = dict()
                    author = info.xpath(".//td[4]/text()")[0].strip()
                    degreeTime = info.xpath(".//td[@align='center']/text()")[0].strip()
                    degreeType = info.xpath(".//td[@align='center']/text()")[1].strip()
                    item[info.xpath(".//td[@class='name']/a/@href")[0]] = [author, degreeTime, degreeType]
                    articles_infos.update(item)
                
                while current < total:
                    current += 1
                    url = "https://navi.cnki.net/knavi/degreeunits/%s/page/articles" % sid
                    params = {
                        "pcode": data["pcode"],
                        "baseId": data["baseid"],
                        "subCode":sid,
                        "scope": quote(data["degree_type"]),
                        "orderBy": "RT|DESC",
                        "pIdx": current - 1
                    }   
                    subject_params =  urlencode(params).replace('%27', '%22')
                    current_app.logger.info(f' 第{current}页 数据获取 --ing   ')
                    while True:
                        sourceResponse = crq.post(url, headers=headers, data=subject_params ) # proxies=self.settings.get("proxies")
                        if not sourceResponse:
                            sid = retrySid(crq, start_url + das, headers)
                            url = f"https://navi.cnki.net/knavi/degreeunits/{sid}/articles"
                        else:
                            break
                    if sourceResponse:
                        sourceResp = etree.HTML(sourceResponse)
                        infos =  sourceResp.xpath("//table[@class='tableStyle']/tbody/tr")
                        for info in infos:
                            item = dict()
                            author = info.xpath(".//td[4]/text()")[0].strip()
                            degreeTime = info.xpath(".//td[@align='center']/text()")[0].strip()
                            degreeType = info.xpath(".//td[@align='center']/text()")[1].strip()
                            item[info.xpath(".//td[@class='name']/a/@href")[0]] = [author, degreeTime, degreeType]
                            articles_infos.update(item)

                    for href, infos in articles_infos.items():  

                        saveData = dict()
                        print("请求详情页面")
                        finalResponse = crq.get(href)   
                        finalResp = etree.HTML(finalResponse)
                    
                        # 学科
                        if finalResp.xpath("//span[@class='rowtit' and contains(text(), '学科专业：')]/../p/text()"):
                            subject = finalResp.xpath("//span[@class='rowtit' and contains(text(), '学科专业：')]/../p/text()")[0]
                            data["subject"] = subject
                        
                        
                        # 标题
                        if finalResp.xpath("//div[@class='doc-title']/span/text()") or finalResp.xpath("//h1//text()"):
                            titleInfos = finalResp.xpath("//div[@class='doc-title']/span/text()") or finalResp.xpath("//h1//text()")
                            saveData["title"] =  "".join(titleInfos)
                        # saveData["title"] = "".join(finalResp.xpath("//h1//text()")[0]) if finalResp.xpath("//h1//text()") else ""
                        if not saveData.get("title"):
                            continue
                        checkResult = cm.schoolPaperFind({"title":saveData["title"], "company": data["name"]})

                        if list(checkResult) != []:
                            current_app.logger.info(f'数据重复：{saveData["title"]}')
                            continue
                        
                        # 作者 
                        if finalResp.xpath("//a[@class='author']/text()"):
                            authors = finalResp.xpath("//a[@class='author']/text()")[0]
                            saveData["author"] = authors
                        else:
                            saveData["author"] = infos[0]
                            
                        # 导师
                        if finalResp.xpath("//span[contains(text(), '导师')]"):
                            mentor = finalResp.xpath("//span[contains(text(), '导师')]/../p/text()")[0].strip() if  finalResp.xpath("//span[contains(text(), '导师')]/../p/text()") else ""
                        elif  finalResp.xpath("//p[contains(text(), '导师')]"):
                            mentor = finalResp.xpath("//p[contains(text(), '导师')]/..//p/text()")[1].strip() if finalResp.xpath("//p[contains(text(), '导师')]/..//p/text()") else ""
                        else:
                            mentor = ""
                        saveData["mentor"] = mentor
                            
                        # 摘要
                        if finalResp.xpath("//*[@id='abstract_text']/@value"):
                            summary = finalResp.xpath("//*[@id='abstract_text']/@value")[0]
                        elif finalResp.xpath("//*[contains(text(), '摘要')]/../span[2]/text()"):
                            summary = finalResp.xpath("//*[contains(text(), '摘要')]/../span[2]/text()")[0]
                        else:
                            summary = ""
                        saveData["summary"] = summary

                        # 关键词
                        if finalResp.xpath("//div[@class='brief']//p[@class='keywords']/a/text()"):
                            keywords = finalResp.xpath("//div[@class='brief']//p[@class='keywords']/a/text()")
                            keywords = [x.strip() for x in keywords]
                            saveData['keywords'] = keywords

                        # 专辑
                        if finalResp.xpath("//span[@class='rowtit' and contains(text(), '专辑：')]/../p/text()"):
                            collection = finalResp.xpath("//span[@class='rowtit' and contains(text(), '专辑：')]/../p/text()")[0]
                            saveData["collection"] = collection
                        
                        # 专题
                        if finalResp.xpath("//span[@class='rowtit' and contains(text(), '专题：')]/../p/text()"):
                            topic = finalResp.xpath("//span[@class='rowtit' and contains(text(), '专题：')]/../p/text()")[0]
                            saveData["topic"] = topic
                        
                        # DOI
                        if finalResp.xpath("//span[@class='rowtit' and contains(text(), 'DOI：')]/../p/text()"):
                            DOI = finalResp.xpath("//span[@class='rowtit' and contains(text(), 'DOI：')]/../p/text()")[0]  
                            saveData["doi"] = DOI
                        
                        # 分类号
                        if finalResp.xpath("//span[@class='rowtit' and contains(text(), '分类号：')]/../p/text()"):
                            type_code = finalResp.xpath("//span[@class='rowtit' and contains(text(), '分类号：')]/../p/text()")[0]  
                            saveData["type_code"] = type_code
                        
                        # 网络出版时间
                        if finalResp.xpath("//script[contains(text(), 'randerDejournalInfo')]/text()"):
                            msg = finalResp.xpath("//script[contains(text(), 'randerDejournalInfo')]/text()")[0]
                            if re.findall(r"randerDejournalInfo(.*)?;", msg):
                                public_time = re.findall(r"randerDejournalInfo(.*)?;", msg)[0]
                                saveData["public_time"] = public_time
                        
                        # 论文大小
                        if finalResp.xpath("//p[@class='total-inform' ]/span[contains(text(), '大小：')]/text()"):
                            size = finalResp.xpath("//p[@class='total-inform' ]/span[contains(text(), '大小：')]/text()")[0].replace("大小：", "").strip()
                            saveData["size"] = size
                        
                        # 页码数
                        if finalResp.xpath("//p[@class='total-inform' ]/span[contains(text(), '页数：')]/text()"):
                            pageno = finalResp.xpath("//p[@class='total-inform' ]/span[contains(text(), '页数：')]/text()")[0].replace("页数：", "").strip()
                            saveData["pageno"] = pageno

                        # 下载数
                        if finalResp.xpath("//p[@class='total-inform' ]/span[contains(text(), '下载：')]/text()"):
                            downloadNum = finalResp.xpath("//p[@class='total-inform' ]/span[contains(text(), '下载：')]/text()")[0].replace("下载：", "").strip()
                            saveData["download_count"] = downloadNum
                        
        
                        saveData["company"] = data["name"]
                        saveData["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
                        saveData["degree_type"] = infos[-1]
                        saveData["degree_year"] = infos[1]
                        saveData["source_type"] = "cnki"
                        saveData["page_link"] = href

                        # print(saveData)
                        Kproducer.sendMsg("cnki_degree", saveData)
                        cm.schoolPaperInsert(saveData)
                        current_app.logger.info(f' 学校名称：{data["name"]}  录入论文：{saveData["title"]}')

                    articles_infos.clear()
                    
  
def reciveData():
    
 
    cao = CAopceptor()
    cao.setTopic("cnki_degree")
    
    if not cao.ConnectKafka("CNKI_DEGREE"):
        current_app.logger.info("unable to connect to Kafka server")
        exit(2)
    
    cao.ProcessKafkaData(None)
    try:
        cao.InsertElasticKafka()
    except Exception as e:
        print(e)
    print("exit ")
    return None
    
        