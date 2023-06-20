import scrapy
import datetime, math
from urllib.parse import urlencode, urljoin
from ..items import SchoolUnitItem
from anti_useragent import UserAgent
import requests
from lxml import etree

from ..pipelines import CnkiDegreePipeline

class DegreeSpider(scrapy.Spider):
    
    name = "degreeArticles"
    # allowed_domains = ["https://www.cnki.net/"]
    base_url = "https://navi.cnki.net/"
    start_url = "https://navi.cnki.net/knavi/degreeunits/subjects"
    ua = UserAgent()
    
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
            
    
    def parse(self, response):
        
        print(response.text)
        