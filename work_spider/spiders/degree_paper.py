import scrapy
from urllib.parse import urlencode, urljoin
from urllib.parse import quote
import requests
from lxml import etree
from scrapy.utils.project import get_project_settings

from ..items import articleCheckItem, articlesItem
from ..pipelines import CnkiDegreePipeline

class DegreeSpider(scrapy.Spider):
    
    name = "degree_paper"
    start_url = "https://navi.cnki.net/knavi/degreeunits/subjects?"
    settings = get_project_settings()

    
    def start_requests(self):
        
        cursor = CnkiDegreePipeline()
        datas = cursor.enumerate_data()
        for data in datas:
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
            yield scrapy.Request(self.start_url + das, headers=headers, meta={"data":data, "headers":headers})
    
    def parse(self, response):
        self.subject_dict = dict()
        subjects = response.xpath("//ul[@class='refirstlayer clearfix']/div/li")
        for sub_ele  in subjects:
            if sub_ele.xpath(".//dl[@class='resecondlayer']"):
                next_subj_infos =  sub_ele.xpath(".//dl[@class='resecondlayer']")
                for next_subj  in next_subj_infos:
                    next_subj_title = next_subj.xpath("./dd/p/b/@title").extract_first() 
                    next_subj_id = next_subj.xpath("./dd/p/b/@id").extract_first() 
                    self.subject_dict[next_subj_id] = next_subj_title
                    if next_subj.xpath(".//span/a"):
                        final_subj_infos =  next_subj.xpath(".//span/a")
                        for final_subj in final_subj_infos:
                            final_subj_title = final_subj.xpath("./@title").extract_first() 
                            final_subj_id = final_subj.xpath("./@id").extract_first() 
                            self.subject_dict[final_subj_id] = final_subj_title
    
            else:
                print("请求页面报错")

        for sid, stitle in self.subject_dict.items():
            
            url = f"https://navi.cnki.net/knavi/degreeunits/{sid}/articles"
            subject_params = {
                "pcode": response.meta["data"]["pcode"],
                "baseId": response.meta["data"]["baseid"],
                "orderBy": "RT|DESC",
                "scope": quote(response.meta["data"]["degree_type"]),
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Host":"navi.cnki.net",
                "Referer":f"https://navi.cnki.net/knavi/degreeunits/{response.meta['data']['baseid']}/detail?uniplatform=NZKPT", 
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                }
            subject_params =  urlencode(subject_params).replace('%27', '%22')
            metas = response.meta["data"]
            metas["sid"] = sid
            metas["stitle"] = stitle
            yield scrapy.Request(url, headers=headers, method="POST", body=subject_params, callback=self.parse_page, meta={"data":metas, "headers":headers})
        
        

    def parse_page(self, response):
        current = 1
        articles_infos = dict()
        total = response.xpath("//*[@id='pageCount']/@value").extract_first("")
        if total:
            total = int(total)
            
            infos = response.xpath("//div[@class='searchresult-list']//table/tbody/tr")
            infos = {x.xpath(".//td[@class='name']/a/@href").extract_first("") : x.xpath(".//td[@class='name']/a/text()").extract_first("")  for x in infos}
            articles_infos.update(infos)
            
            while current < total:
                current += 1
                url = "https://navi.cnki.net/knavi/degreeunits/%s/page/articles" % response.meta["data"]["sid"]
                params = {
                    "pcode": response.meta["data"]["pcode"],
                    "baseId": response.meta["data"]["baseid"],
                    "subCode": response.meta["data"]["sid"],
                    "scope": quote(response.meta["data"]["degree_type"]),
                    "orderBy": "RT|DESC",
                    "pIdx": current - 1
                }   
                subject_params =  urlencode(params).replace('%27', '%22')
                resp = requests.post(url, headers=response.meta["headers"], data=subject_params ) # proxies=self.settings.get("proxies")
                if resp.text:
                    xmlobj = etree.HTML(resp.text)
                    infos = xmlobj.xpath("//div[@class='searchresult-list']//table/tbody/tr")
                    infos = {x.xpath(".//td[@class='name']/a/@href")[0]: x.xpath(".//td[@class='name']/a/text()")[0]  for x in infos}
        
        for href, title in articles_infos.items():  
            checkitem = articleCheckItem()
            checkitem["title"] = title
            # yield checkitem
            # if checkitem["isExist"]:     
            yield  scrapy.Request(href, headers=response.meta["headers"],  callback=self.parse_detail, meta={"data":response.meta["data"] })
       

    def parse_detail(self, response):
        
        data = articlesItem()
        
        if response.xpath("//span[@class='rowtit' and contains(text(), '学科专业：')]/../p/text()"):
            subject = response.xpath("//span[@class='rowtit' and contains(text(), '学科专业：')]/../p/text()")[0]
            data.subject = subject
        
        
        # 摘要
        if response.xpath("//*[@id='abstract_text']/@value"):
            summary = response.xpath("//*[@id='abstract_text']/@value")[0]
            data.summary = summary

        # 关键词
        if response.xpath("//div[@class='brief']//p[@class='keywords']/a/text()"):
                keywords = response.xpath("//div[@class='brief']//p[@class='keywords']/a/text()")
                keywords = [x.strip() for x in keywords]
                data.keywords = keywords

        # 专辑
        if response.xpath("//span[@class='rowtit' and contains(text(), '专辑：')]/../p/text()"):
            collection = response.xpath("//span[@class='rowtit' and contains(text(), '专辑：')]/../p/text()")[0]
            data.collection = collection
        
        # 专题
        if response.xpath("//span[@class='rowtit' and contains(text(), '专题：')]/../p/text()"):
            topic = response.xpath("//span[@class='rowtit' and contains(text(), '专题：')]/../p/text()")[0]
            data.topic = topic
        
        # DOI
        if response.xpath("//span[@class='rowtit' and contains(text(), 'DOI：')]/../p/text()"):
            DOI = response.xpath("//span[@class='rowtit' and contains(text(), 'DOI：')]/../p/text()")[0]  
            data.doi = DOI
        
        # 分类号
        if response.xpath("//span[@class='rowtit' and contains(text(), '分类号：')]/../p/text()"):
            type_code = response.xpath("//span[@class='rowtit' and contains(text(), '分类号：')]/../p/text()")[0]  
            data.type_code = type_code
        
        # 网络出版时间
        if response.xpath("//script[contains(text(), 'randerDejournalInfo')]"):
            msg = response.xpath("//script[contains(text(), 'randerDejournalInfo')]/text()")[0]
            if re.findall(r"randerDejournalInfo(.*)?;", msg):
                public_time = re.findall(r"randerDejournalInfo(.*)?;", msg)[0]
                data.public_time = public_time
                
        
        # 论文大小
        if response.xpath("//p[@class='total-inform' ]/span[contains(text(), '大小：')]/text()"):
            size = response.xpath("//p[@class='total-inform' ]/span[contains(text(), '大小：')]/text()")[0].replace("大小：", "").strip()
            data.size = size
        
        # 页码数
        if response.xpath("//p[@class='total-inform' ]/span[contains(text(), '页数：')]/text()"):
            pageno = response.xpath("//p[@class='total-inform' ]/span[contains(text(), '页数：')]/text()")[0].replace("页数：", "").strip()
            data.pageno = pageno

        
        