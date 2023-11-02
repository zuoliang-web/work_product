
from mongoengine import *
from elasticsearch_dsl import  Date, InnerDoc, Keyword, Text, Integer, Object, analyzer, tokenizer, Index, analysis, Double, Long, Completion

import elasticsearch_dsl

def _not_empty(val):
    if not val:
        raise ValidationError('value can not be empty')

class Degree(Document):
    """
        学校主体
    """
    
    _id = StringField() #IntField(max_length=25) 
    area = StringField(max_length=50)  # 学校所属地  
    name = StringField(validation=_not_empty)  # 学校名称
    artical_counts = StringField(validation=_not_empty) # 学校-文献篇数
    citel_counts = StringField() # 学校-总被引次数
    download_counts = StringField()  # 学校-总下载次数
    img_path = ListField(default=[])  # 学校 图片
    tags = StringField()  # 学校标签
    baseid = StringField() # baseid 
    source = StringField() # 数据来源
    path = StringField() #  页面链接
    create_time = StringField()   # 录入日期
    degree_type = StringField() #  收藏的文献级别
    pcode = StringField()  # pcode
   

    meta = {"collection":"test_degree"}
 


class DegreeArticle(Document):
    """
        学位论文
    """
    
    degree_size = ("master", "doctor") 
    
    _id = StringField() #IntField(max_length=25) 
    subject = StringField(max_length=50)  # 学科  
    title = StringField(validation=_not_empty)  # 论文标题
    author = StringField(validation=_not_empty) # 作者
    mentor = StringField() # 导师
    summary = StringField()  # 论文摘要
    keywords = ListField(default=[])  # 论文关键词
    collection = StringField()  # 专辑
    topic = StringField() # 专题 
    doi = StringField() # DOI
    type_code = StringField() # 分类号
    public_time = StringField()   # 网络出版日期
    size = StringField() # 文章大小
    pageno = StringField()  # 页码数
    download_num = IntField()  # 下载次数
    company =  StringField()  # 学校
    create_time = StringField()   # 录入日期
    degree_type = StringField(max_length=10, choices=degree_size) # 论文级别
    degree_year = StringField()   # 学位授予年度
    source_type = StringField()  # 数据来源
    page_link = StringField() # 页面链接
    
    # type_code = StringField() # 分类号
    # journal_name = StringField() # 论文主体
    # quote_num = IntField()  # 引用次数

    meta = {"collection":"test_degree_articles"}
    


class ElasticDegree(elasticsearch_dsl.Document):
    """
        没有找到合适的创建分析器的api, 所以只做初始化用
        后续会使用
    """
    # common
    
    id = Text()
    
    # aggs = Object(Agg, required=True)
    # suggest = Object(Suggest, required=True)
    
    area = Keyword()              #   
    name =  Text()                # 学校名称  
    artical_counts = Integer()    # 文章数
    
    pubtype = Keyword()                # 类型区分
    region = Keyword()                 # 省市区域
    source  = Keyword()                # 数据来源 【cnki】
    status = Long()                    # 状态
    
    enname =  Keyword()             # 英文
    article_count = Integer()       # 文章数
    download_count = Integer()      # 下载数
    quote_count = Integer()         # 引用次数
    fundpaper_numbers =  Integer()  # 基金论文量
    
    journal_img =  Text()           # 封面图片
    journal_name = Text()           # 期刊名称
    
    tags = Keyword(multi=True)      # 标签
    journal_collection =  Text()      # 专辑
    journal_topic =  Text()          # 专题
    address = Text()                # 地址
    
    create_time =  Date(format="yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis")   # 创建日期
    update_time = Date(format="yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis")  # 更新日期
    
    
    class Index:
        name = 'journals_degree'
    
class Agg(elasticsearch_dsl.InnerDoc):
    journal_collection = Keyword(multi=True) 
    journal_create = Keyword()
    journal_topic = Keyword(multi=True) 
    publish_company = Keyword()
    publish_frequency = Keyword()
    pubtype = Keyword()
    region = Keyword()
    source = Keyword()  

class Suggest(elasticsearch_dsl.InnerDoc):
    journal_collection = Completion()       # 专辑
    journal_name = Completion()             # 期刊名称
    journal_topic = Completion()            # 专辑       
    publish_company = Completion()            # 主办单位    
    
    
    

   
    