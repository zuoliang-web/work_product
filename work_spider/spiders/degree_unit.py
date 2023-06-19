import scrapy
import datetime, math
from urllib.parse import urlencode, urljoin
from ..items import SchoolUnitItem
from anti_useragent import UserAgent

class DegreeSpider(scrapy.Spider):
    
    name = "degree_unit"
    # allowed_domains = ["https://www.cnki.net/"]
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
        
        yield scrapy.Request(self.start_url,method="POST",body=das ,headers=headers ,callback=self.parse ,meta = {"current_page":1,"params": params, "headers": headers, "schoolDict":{}})
        
    
    def parse(self, response):
        
        
        total_count =  response.xpath("//span[@class='totalcount']/em/text()").extract_first("")
        current_page = response.meta["current_page"]
        schoolInfo = response.xpath("//ul[@class='list_tup']/li")
        
        for item in schoolInfo:  
            href = urljoin(self.base_url, item.xpath("./a/@href").extract_first(""))
            baseid = href.split("baseid=")[-1]
            headers = {"User-Agent": self.ua.random}
            path = f"https://navi.cnki.net/knavi/degreeunits/{baseid}/detail?uniplatform=NZKPT"
            yield scrapy.Request(path,method="GET", headers=headers, meta = {"baseid": baseid}, callback=self.parse_detail)
             
        try:   
            if int(current_page) < int(total_count):
                response.meta["params"]["switchdata"] = ""
                response.meta["params"]["pageindex"] = str(current_page)
                current_page += 1
                das = urlencode(response.meta["params"]).replace('%27', '%22')
                yield scrapy.Request(self.start_url,method="POST",body=das ,headers=response.meta["headers"] ,callback=self.parse ,meta = {"current_page": current_page,"params": response.meta["params"] , "headers": response.meta["headers"]}, dont_filter=True)
        except Exception as e:
            print(e)
    

        
    
    def parse_infos(self, response):
        
        
            
        schoolDict =  response.meta["schoolDict"]
               
        
        for key, value in schoolDict.items():
            
            
            headers = {"User-Agent": self.ua.random}
            baseid = value[-1]
            path = f"https://navi.cnki.net/knavi/degreeunits/{baseid}/detail?uniplatform=NZKPT"

            yield scrapy.Request(path,method="GET", headers=headers, meta = {"baseid": baseid}, callback=self.parse_detail)
    

    def parse_detail(self, response):
        
        item = SchoolUnitItem()
        

        area = response.xpath("//p[@class='hostUnit']/span/text()").extract_first("").strip()
        name = response.xpath("//h3[@class='titbox']/text()").extract_first("").strip()
        artical_counts = response.xpath("//p[@class='hostUnit']/span/text()").extract_first("")
        citel_counts = response.xpath("//p[@class='hostUnit']/span/text()").extract_first("")
        download_counts = response.xpath("//p[@class='hostUnit']/span/text()").extract_first("")
        img_path = response.urljoin(response.xpath("//*[@id='J_journalPic']/img/@src").extract_first(""))
        tags = response.xpath("//h3[@class='titbox']/span/text()").extract_first("")
        
        if not name:
            headers = {"User-Agent": self.ua.random}
            path = f"https://navi.cnki.net/knavi/degreeunits/{response.meta['baseid']}/detail?uniplatform=NZKPT"
            yield scrapy.Request(path,method="GET", headers=headers, meta = {"baseid": response.meta['baseid']}, callback=self.parse_detail)
        else:
            item["area"] = area
            item["name"] = name
            item["artical_counts"] = artical_counts
            item["citel_counts"] = citel_counts
            item["download_counts"] = download_counts
            item["img_path"] = img_path
            item["tags"] = tags
            item["baseid"] =  response.meta["baseid"]
            item["source"] = "CNKI" 
            item["path"] = response.url
            item["create_time"] = datetime.datetime.now()
            yield item



if __name__ == "__main__":
    
    
    import requests
    start_url = 'https://navi.cnki.net/knavi/degreeunits/searchbaseinfo'

  
    
  