import os, sys

from configparser import ConfigParser 
import pymysql
from pymysql.converters import escape_string

from flask_sqlalchemy import SQLAlchemy
mysql_db = SQLAlchemy()

from .. import conf





class Cmysql:
    
    
    def __init__(self):
        
        self.config = { 
        'host': conf.get("mysql", "host"), 
        'port': int(conf.get("mysql", "port")),  
        'user': conf.get("mysql", "user"), 
        'password': conf.get("mysql", "password"),
        'db': conf.get("mysql", "db1"),
        'charset':'utf8',         
        'cursorclass':pymysql.cursors.DictCursor, 
        # 游标设置为字典类型默认值为pymysql.cursors.Cursor。
    }    
         
    def __conn__(self):
        
        self.connection = pymysql.connect(**self.config)
   
        
    def putData(self, tab_name, item, year):
        self. __conn__()
        isExist = f"show tables like '{tab_name}'; "
        
        values = item.values.tolist()
        columns = item.columns.tolist()
        key_lists = ",".join(["`%s`" % x for x in  columns]) 
        try:
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor()  
            cursor.execute(isExist)
            result = cursor.fetchone()
        except Exception as e:
            print(f"查询表{tab_name}信息失败： ", e)
            cursor.close()
              
            return False
        
        
        if not result:
            
            create_tab_sql_head = "create table %s( id int(8) primary key auto_increment  comment '主键id',create_time date comment '年份', " % tab_name
            create_tab_sql_body = ",".join([f"{x} varchar(200) " for x in columns ])
            create_tab_sql_end = ")"       

            try:
                self.connection.ping(reconnect=True)
                creat_tab_sql = create_tab_sql_head + create_tab_sql_body + create_tab_sql_end
                cursor.execute(creat_tab_sql)
                self.connection.commit()
            except Exception as e :
                print(f"创建表{tab_name}信息失败： ", e)
                cursor.close()
                
                return False
        

        sql = "insert into %s(%s) VALUES(%s)" % (tab_name, key_lists, ",".join(["%s" for x in range(len(columns))]))
        item_data = [ tuple("" if x == "nan" or x == "0.0" else escape_string(str(x)) for x in result)    for result in values]
        try:
            
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor()
            cursor.executemany(sql, item_data)
            self.connection.commit()
            
        except Exception as e:
            print(f"更新表{tab_name}数据失败： ", e)
            self.connection.rollback()
            cursor.close()
            return False

        modif_sql = "update %s set create_time = '%s'" % (tab_name, year+"-01-01")
        try:
            
            self.connection.ping(reconnect=True)
            cursor.execute(modif_sql)
            self.connection.commit()
        except Exception as e:
            print(f"{tab_name}修改年份失败： ", e)
            self.connection.rollback()
            cursor.close()
            return False
        return True


    def query(self, sql):
        
        try:
            self.__conn__()
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor()  
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"查询表信息失败： ", e)
            cursor.close()           
            return None
    
    def commit(self, sql):
        try:
            self.__conn__()
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor()  
            cursor.execute(sql)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"添加数据失败： ", e)
            self.connection.rollback()    
            cursor.close()           
            return None
        
    def check_isexist(self, sql):
        try:
            self.__conn__()
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor()  
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                return None
        except Exception as e:
            print(f"查询数据是否重复,sql失败： ", e) 
        finally:
            cursor.close()   
                
        return True
    
    def exit(self):
        try:
            self.connection.close()
        except Exception:
            pass
        
        