import scrapy
from urllib.parse import urlencode, urljoin
from urllib.parse import quote

from ..pipelines import CnkiDegreePipeline

class DegreeSpider(scrapy.Spider):
    
    name = "degree_paper"
    start_url = "https://navi.cnki.net/knavi/degreeunits/subjects?"
   
    
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
            
            yield scrapy.Request(url, headers=headers, method="POST", body=subject_params, callback=self.parse_detail)
        print(1)
        

    def parse_detail(self, response):
        total = response.xpath("//*[@id='maxCount']/@value").extract_first("")
        if total:
            total = int(total)
            
            infos = response.xpath("//div[@class='searchresult-list']//table/tbody/tr")
            infos = {x.xpath(".//td[@class='name']/a/@href").extract_first("") : x.xpath(".//td[@class='name']/a/text()").extract_first("")  for x in infos}

             
        print(1)