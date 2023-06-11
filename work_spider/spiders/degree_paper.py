import scrapy

class DegreeSpider(scrapy.Spider):
    
    name = "degree_paper"
    allowed_domains = ["https://www.cnki.net/"]
    
    
    def parse(self):
        
        pass