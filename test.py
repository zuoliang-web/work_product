import pymongo
import pymysql

MONGO_USER = "root"
MONGO_PASSWD = "abcd1234"
MONGO_HOST = "192.168.0.120"
MONGO_PORT = "27017"
MONGO_DB = "school_data"
SEL_write_TAB = "journals"
client = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(MONGO_USER, MONGO_PASSWD, MONGO_HOST, int(MONGO_PORT)))
db = client[MONGO_DB]
col = db[SEL_write_TAB] 


config = { 
            'host':'192.168.0.120', 
            'port':13709, 
            'user':'elang_user', 
            'password':'elang_backup123', 
            'db':'worldwide', 
            'charset':'utf8',         
            'cursorclass':pymysql.cursors.DictCursor, 
            # 游标设置为字典类型默认值为pymysql.cursors.Cursor。
        } 
connection = pymysql.connect(**config)


result = col.find_one({"journal_name":"现代城市研究"})

modif_sql = """
    update Modern_Urban_Research set journal_name='现代城市研究', pubtype='%s',  baseid='%s',journal_topic='%s',enname='%s',region='%s',lang='%s',
    source_type='cnki',  publish_company='%s', journal_cn='%s', journal_issn='%s', journal_img='%s', status=1, journal_collection='%s'
""" % (
    result["pubtype"],result["baseid"],result["journal_topic"],result["enname"],result["region"],result["lang"],
    result["publish_company"],result["journal_cn"],result["journal_issn"],result["journal_img"], result["journal_collection"]
)
cursor = connection.cursor()
cursor.execute(modif_sql)
connection.commit()
print(modif_sql)