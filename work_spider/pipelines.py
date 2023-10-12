# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
from itemadapter import ItemAdapter
import pymongo
from scrapy.exceptions import DropItem

from scrapy.utils.project import get_project_settings
from .items import SchoolCheckItem, articleCheckItem, SchoolUnitItem, articlesItem




class WorkSpiderPipeline:
    def process_item(self, item, spider):
        return item


class CnkiDegreePipeline:
    
    
    def __init__(self):
        # 连接数据库
        settings = get_project_settings()
        self.client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(settings.get('MONGO_INFOS')["MONGO_USER"], settings.get('MONGO_INFOS')["MONGO_PASSWD"], settings.get('MONGO_INFOS')["MONGO_HOST"], int(settings.get("MONGO_INFOS")["MONGO_PORT"])))
        self.db = self.client[settings.get('MONGO_INFOS')["MONGO_DB"]]
        self.coll = self.db[settings.get("MONGO_INFOS")["DEGREE_UNIT"]]  
        self.art_coll = self.db[settings.get("MONGO_INFOS")["DEGREE_ARTICLES"]]
   
    
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:       
            if type(item) == SchoolCheckItem:
                if self.coll.find_one({"baseid":dict(item)["baseid"]}):
                    print(f"{dict(item)['baseid']}: 已存在")
                    item["isExist"] = False
                else:
                    item["isExist"] = True
            elif type(item) == articleCheckItem:           
                if self.art_coll.count_documents({"title":dict(item)["title"]}) != 0:
                    spider.logger.info(f" 学校：{dict(item)['company']} 论文： {dict(item)['title']}: 已存在")
                    item["isExist"] = False
                else:
                    item["isExist"] = True
                
            elif type(item) == SchoolUnitItem:
                self.coll.insert(dict(item))             # 将item解包后存入mongodb中
                print(f"{dict(item)['name']}: 已录入")
            elif type(item) == articlesItem:
                self.art_coll.insert(dict(item))
                now_time = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
                spider.logger.info(f"时间：{now_time}   学校：{dict(item)['company']} 论文： {dict(item)['title']}  已录入")                
        return item
    
    
    def  enumerate_data(self):
        
        data = self.coll.find(no_cursor_timeout=True).skip(3)
        return data

