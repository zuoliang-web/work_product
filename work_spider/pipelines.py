# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from scrapy.exceptions import DropItem
from .settings import MONGO_USER, MONGO_PASSWD, MONGO_DB, MONGO_COL, MONGO_PORT, MONGO_HOST

class WorkSpiderPipeline:
    def process_item(self, item, spider):
        return item


class CnkiDegreePipeline:
    def __init__(self):
        # 连接数据库
        self.client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(MONGO_USER, MONGO_PASSWD, MONGO_HOST, int(MONGO_PORT)))
        self.db = self.client[MONGO_DB]
        self.coll = self.db[MONGO_COL]  
    
    
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            print("insert ---=================")
            
            if self.coll.find({"baseid":dict(item)["baseid"]}):
                return None
            self.coll.insert(dict(item))  # 将item解包后存入mongodb中
        return item
    