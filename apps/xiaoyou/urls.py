import os, json
from flask import Flask, request
from flask import Blueprint, jsonify

from models.degree import ElasticDegree

spiders = Blueprint("spiders", __name__)



# 导航页面数据
@spiders.route("/getSearchData", methods=["POST"])
def getSearchData():
    paramsData = request.args.to_dict()
    if paramsData is None or paramsData == "":
        return jsonify({'status': 403, "message":"Parameter set_config can not be empty"})
    paramsJsonData = json.loads(paramsData)
    print(paramsJsonData)                   
    
    
    ElasticDegree.get("")
    
    return jsonify({'status': 200, "message":"spider successful"})

