# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from scrapy.exceptions import DropItem

from scrapy.utils.project import get_project_settings
from .settings import MONGO_USER, MONGO_PASSWD, MONGO_DB, MONGO_COL, MONGO_PORT, MONGO_HOST


settings = get_project_settings()

class WorkSpiderPipeline:
    def process_item(self, item, spider):
        return item


class CnkiDegreePipeline:
    
    
    def __init__(self):
        # 连接数据库
        settings['MONGO_PORT']
        settings = get_project_settings()
        self.client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(settings['MONGO_USER'], settings['MONGO_PASSWD'], settings['MONGO_HOST'], int(settings['MONGO_PORT'])))
        self.db = self.client[settings['MONGO_DB']]
        self.coll = self.db[settings['DEGREE_UNIT']]  
    
   
    
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            
            
            if self.coll.find_one({"baseid":dict(item)["baseid"]}):
                print(f"{dict(item)['name']}: 已存在")
                return None
            self.coll.insert(dict(item))  # 将item解包后存入mongodb中
            print(f"{dict(item)['name']}: 已录入")
        return item
    
    
    def  enumerate_data(self):
        
        data = self.coll.find(no_cursor_timeout=True).skip(1).limit(3)
        return data


class CnkiDegreeUnitCheckPipeline:
    def __init__(self):
        # 连接数据库
        settings['MONGO_PORT']
        settings = get_project_settings()
        self.client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(settings['MONGO_USER'], settings['MONGO_PASSWD'], settings['MONGO_HOST'], int(settings['MONGO_PORT'])))
        self.db = self.client[settings['MONGO_DB']]
        self.coll = self.db[settings['DEGREE_ARTICLES']]  
    
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            
            
            if self.coll.find_one({"baseid":dict(item)["baseid"]}):
                print(f"{dict(item)['name']}: 已存在")
                return None
            self.coll.insert(dict(item))  # 将item解包后存入mongodb中
            print(f"{dict(item)['name']}: 已录入")
        return item