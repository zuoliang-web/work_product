import os, time
from configparser import ConfigParser
import pymongo
from pymongo.errors import AutoReconnect
# from flask_mongoengine import MongoEngine


# mongo_db = MongoEngine()

from .. import conf



class Cmongo:
    
    def __init__(self):

        self.client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(conf.get("mongodb", "user") ,conf.get("mongodb", "password"), 
                                                                            conf.get("mongodb", "host") , int(conf.get("mongodb", "port"))),
                                          serverSelectionTimeoutMS=10000, socketTimeoutMS=10000)
        self.db = self.client[conf.get("mongodb", "db")]
        
        
    
    def schoolUnitInit(self):
        
        
        self.schoolUnitCol = self.db[conf.get("mongodb", "schoolunit")]

    def schoolPaperInit(self):
        
        
        self.schoolPaperCol = self.db[conf.get("mongodb", "schoolpaper")]
               

    
    def schoolUnitInsert(self, item):
        
        if not hasattr(self,"schoolUnitCol"):
            self.schoolUnitInit()
        try:
            self.schoolUnitCol.insert_one(item)
        except Exception as e:
            print("school unit insert error: ", e)
            
    def schoolUnitFind(self,query=None):
        
        if not hasattr(self,"schoolUnitCol"):
            self.schoolUnitInit()
            
        try:
            if query:
                results = self.schoolUnitCol.find(query,no_cursor_timeout=True)
            else:
                results = self.schoolUnitCol.find(no_cursor_timeout=True)
        except Exception as e:
            print("school unit insert error: ", e)
            return None
        return results

    def schoolPaperFind(self,query=None):
        
        if not hasattr(self,"schoolPaperCol"):
            self.schoolPaperInit()
            
        try:
            print("find start")
            if query:
                with  self.schoolPaperCol.find(query,no_cursor_timeout=True)as cursor:
                    return cursor
            else:
                results = self.schoolPaperCol.find(no_cursor_timeout=True)
            print("find end")
        except Exception as e:
            print("school paper insert error: ", e)
            return None
        return results
    
    def schoolPaperInsert(self, item):
        
        if not hasattr(self,"schoolPaperCol"):
            self.schoolPaperInit()
        try:
            print("insert start")
            self.schoolPaperCol.insert_one(item)
            print("insert end")
        except Exception as e:
            print("school unit insert error: ", e)
   