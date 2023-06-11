import scrapy

class DegreeSpider(scrapy.Spider):
    
    name = "degree_unit"
    allowed_domains = ["https://www.cnki.net/"]
    start_url = "https://navi.cnki.net/knavi/degreeunits/searchbaseinfo"
    
    def start_requests(self):
        
        params = {
            "searchStateJson":{"StateID":"","Platfrom":"","QueryTime":"","Account":"knavi","ClientToken":"","Language":"","CNode":{"PCode":"DEGREE","SMode":"","OperateT":""},"QNode":{"SelectT":"","Select_Fields":"","S_DBCodes":"","QGroup":[],"OrderBy":"RT|","GroupBy":"","Additon":""}},
            "displaymode": 1,
            "pageindex": 1,
            "pagecount": 21,
            "index": "",
            "searchType": "学位授予单位名称",
            "clickName": "",
            "switchdata": "clickTabSearch"
        }
        yield scrapy.Request(self.start_url,method="POST", callback=self.parse)
        
    
    
    def parse(self, response):
        
        xinfos = response.xpath("//div[@class='currentBox']")
        print(1)
        return "ok"