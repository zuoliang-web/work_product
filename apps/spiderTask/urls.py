import os, json
import threading
import datetime
import requests   
from urllib.parse import urljoin, urlencode
from lxml import etree
from flask import Blueprint, jsonify
from pymysql.converters import escape_string

from apps.utils.baseRequest import CRequest


from .view import pressUnit, pressPaper, reciveData

spiders = Blueprint("spiders", __name__)


# 学校主体信息
@spiders.route("/schoolUnit", methods=["GET", "POST"])
def spiderSchoolUnit():
    
    pressUnit()
    return jsonify({'status': 200, "message":"spider successful"})

 
# 学校 —— 论文信息
@spiders.route("/schoolPapaer", methods=["GET", "POST"])
def spiderSchoolPaper():
    
    pressPaper()
    return jsonify({'status': 200, "message":"spider successful"})
 
@spiders.route("/kafkaWorker", methods=["GET", "POST"])
def kafkaCustomer():
    
    reciveData()
    return jsonify({'status': 200, "message":"spider successful"})
 