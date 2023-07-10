import scrapy
from urllib.parse import urlencode, urljoin

from ..pipelines import CnkiDegreePipeline
from ..items import SchoolUnitItem

class DegreeSpider(scrapy.Spider):
    
    name = "journal"
    allowed_domains = ["https://www.cnki.net/"]
    
    
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
            yield scrapy.Request(self.start_url, headers=headers, body=das)
    
    
    def parse(self):
        
        pass