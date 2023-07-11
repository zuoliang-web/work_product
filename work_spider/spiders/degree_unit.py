import scrapy
import datetime, math, time
from urllib.parse import urlencode, urljoin

from anti_useragent import UserAgent
import requests
from lxml import etree

from ..pipelines import CnkiDegreePipeline
from ..items import SchoolUnitItem, SchoolCheckItem
from ..settings import proxies

class DegreeSpider(scrapy.Spider):
    
    name = "degree_unit"
    base_url = "https://navi.cnki.net/"
    start_url = "https://navi.cnki.net/knavi/degreeunits/searchbaseinfo"
    ua = UserAgent()
    
    def start_requests(self):
        
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
        
        yield scrapy.Request(self.start_url, method="POST", headers=headers, body=das, meta={"params":params, "headers":headers})
            
    
    def parse(self, response):
        
        current_page = 2
        params = response.meta["params"]
        schoolDict = {}
        while True:
            
            
            if current_page == 2:
                schoolInfo = response.xpath("//ul[@class='list_tup']/li")  
                for item in schoolInfo:  
                    name = item.xpath(".//div[@class='detials']/h1/text()").extract_first()
                    href = urljoin(self.base_url, item.xpath("./a/@href").extract_first())
                    baseid = href.split("baseid=")[-1]
                    schoolDict[name] = baseid  
            else:
                schoolInfo = xmlobj.xpath("//ul[@class='list_tup']/li")
                for item in schoolInfo:  
                    name = item.xpath(".//div[@class='detials']/h1/text()")[0]
                    href = urljoin(self.base_url, item.xpath("./a/@href")[0])
                    baseid = href.split("baseid=")[-1]
                    schoolDict[name] = baseid
            
            
            params["switchdata"] = ""
            params["pageindex"] = str(current_page)  
            current_page += 1 
            
            das = urlencode(params).replace('%27', '%22')
            if current_page == 3:
                break
            while True:
                try:
                    resp = requests.post(self.start_url, data=das, headers=response.meta["headers"], proxies=proxies)
                
                    if response.text != '<script>window.location.href="/knavi/access/verification"</script>' and resp.status_code == 200:
                        xmlobj = etree.HTML(resp.text)
                        schoolInfo = xmlobj.xpath("//ul[@class='list_tup']/li")
                        if schoolInfo:
                            break
                except Exception as e:
                    time.sleep(0.5)
                    print(e)
            
            
        
        
        for key, value in schoolDict.items():
            path = f"https://navi.cnki.net/knavi/degreeunits/{value}/detail?uniplatform=NZKPT"
            checkitem = SchoolCheckItem()
            checkitem["baseid"] = value
            yield checkitem
            if checkitem["isExist"]:
                yield scrapy.Request(path,  headers=response.meta["headers"], meta={"value":value}, callback=self.parse_detail)
            
            
    def parse_detail(self, response):
        
        data = SchoolUnitItem()
        
        area = response.xpath("//p[@class='hostUnit']/span/text()").extract_first("").strip()
        name = response.xpath("//h3[@class='titbox']/text()").extract_first("").strip()
        artical_counts = response.xpath("//p[@class='hostUnit']/label[contains(text(),'文献篇数')]/../span/text()").extract_first("").replace("篇", "") 
        citel_counts = response.xpath("//p[@class='hostUnit']/label[contains(text(),'总被引次数')]/../span/text()").extract_first("").replace("次", "") 
        download_counts = response.xpath("//p[@class='hostUnit']/label[contains(text(),'总下载次数')]/../span/text()").extract_first("").replace("次", "")
        img_path = "https"+response.xpath("//*[@id='J_journalPic']/img/@src").extract_first("") 
        tags = response.xpath("//h3[@class='titbox']/span/text()").extract_first("") 
        degree_type = response.xpath("//*[@id='J_journalPic']/div[@class='radio']/a/@value").extract_first("") 
        pcode =  response.xpath("//*[@id='pCode']/@value").extract_first("") 
       
        
        data["area"] = area
        data["name"] = name
        data["artical_counts"] = artical_counts
        data["citel_counts"] = citel_counts
        data["download_counts"] = download_counts
        data["img_path"] = img_path
        data["tags"] = tags
        data["baseid"] =  response.meta["value"]
        data["source"] = "CNKI" 
        data["path"] = response.url
        data["create_time"] = datetime.datetime.now()
        data["degree_type"] = degree_type
        data["pcode"] = pcode
        yield data
        
    
    