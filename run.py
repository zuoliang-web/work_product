import os
from flask import Flask
import logging
from logging.handlers import TimedRotatingFileHandler
from configparser import ConfigParser

# from apps.dbutils.CMongo import mongo_db
from apps.spiderTask.urls import spiders

# from apps.db_transt_data.models import mysql_db  as transt_db
# from apps.spiders.models import mysql_db as spider_db


conf = ConfigParser()
BASE_DIR = os.path.dirname(__file__)
config_file = os.path.join(BASE_DIR, "mission.ini")
conf.read(config_file)


app = Flask(__name__)

app.config['SECRET_KEY'] = 'jfiagiisfashjsjf'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://%s:%s@%s:%s/%s" % (conf.get("mysql", "user"), conf.get("mysql", "password"),  
                                                                    conf.get("mysql", "host"), int(conf.get("mysql", "port")),
                                                                    conf.get("mysql", "db") )

app.config['MONGODB_SETTINGS']={   
    'db':  conf.get("mongodb", "db") ,
    'host': conf.get("mongodb", "host"),
    'port': int(conf.get("mongodb", "port")),
    'connect': True,
    'username': conf.get("mongodb", "user"),
    'password':  conf.get("mongodb", "password"),
    "authentication_source":"admin"
}


app.register_blueprint(spiders, url_prefix="/spiders")

formatter = logging.Formatter("[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
handler = TimedRotatingFileHandler("logs/flask.log", when="D", interval=1, backupCount=15, encoding="UTF-8", delay=False, utc=True)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
handler.setFormatter(formatter)

# transt_db.init_app(app)
# mongo_db.init_app(app)


@app.route("/")
def home():
    return "welcome home"



if __name__ == "__main__":
    
    # print(app.url_map)
    app.run(host="0.0.0.0", port=8979, debug=False)
    
    
    # 
    
    
    