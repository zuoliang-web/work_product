import os, time
import requests
from configparser import ConfigParser 
from anti_useragent import UserAgent
from urllib.parse import urljoin
from flask import current_app

from .commFunc import coverGapTouilet

from .. import conf

ua = UserAgent()

class  CRequest:
    
    
    def __init__(self):
        
        self.proxyMeta =  "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host" : conf.get("proxyinfo", "host"), 
            "port" : int(conf.get("proxyinfo", "port")), 
            "user" : conf.get("proxyinfo", "user"), 
            "pass" : conf.get("proxyinfo", "password"),
        }
        self.proxies = {
        "http": self.proxyMeta,
        "https": self.proxyMeta,
        }
        self.switchProxyURL = "http://%s/simple/switch-ip?username=%s&password=%s" % (conf.get("proxyinfo", "host"), conf.get("proxyinfo", "user"), conf.get("proxyinfo", "password"))
        self.session = requests.Session()
        
    
    def get(self, url, headers=None,data=None):
        
        self.retry = 7
        if not headers:
            headers = {"User-Agent": ua.random}
        elif not headers.get("User-Agent"):
            headers["User-Agent"] = ua.random
        while True:
            
            try:
                if self.retry > 4:
                    if not data:
                        response = self.session.get(url, headers=headers,  proxies=self.proxies,timeout=20)
                    else:
                        response = self.session.get(url, headers=headers, params=data,  proxies=self.proxies,timeout=20)
                elif  self.retry > 0:
                    if not data:
                        response = self.session.get(url, headers=headers,timeout=20)
                    else:
                        response = self.session.get(url, headers=headers, params=data,timeout=20)
                else:
                    current_app.logger.info("get请求 重试次数达到上限， 进行切换ip")
                    requests.get(self.switchProxyURL)
                    time.sleep(8)
                    self.retry = 7
                         
                if response.status_code == 200 and response.text:
                    
                    if response.encoding == "ISO-8859-1":
                        try:
                            result = response.text.encode("ISO-8859-1").decode("utf-8")
                        except Exception as e:
                            current_app.logger.info("uncode error", e)
                            return None
                    else:
                        result = response.text
                        
                    if "知网节超时验证"  in   result:
                        print(1)
                        while   True:
                            result = coverGapTouilet(url)
                            if result:
                                break
                    return result
                else:
                    self.retry -= 1
                
                    
            except Exception as e:
                print("error", e)
                self.retry -= 1
                # return None            
            
            
    def post(self, url, headers=None,data=None):
            
        self.retry = 7
        if not headers:
            headers = {"User-Agent": ua.random}
        elif not headers.get("User-Agent"):
            headers["User-Agent"] = ua.random
        while True:
            
            try:
                if self.retry > 4:
                    if not data:
                        response = self.session.post(url, headers=headers,  proxies=self.proxies)
                    else:
                        response = self.session.post(url, headers=headers, data=data,  proxies=self.proxies)
                elif  self.retry > 0:
                    if not data:
                        response = self.session.post(url, headers=headers)
                    else:
                        response = self.session.post(url, headers=headers, data=data)
                else:
                    current_app.logger.info("post请求 重试次数达到上限， 进行切换ip")
                    requests.get(self.switchProxyURL)
                    time.sleep(8)
                    self.retry = 7
                 
                if response.status_code == 200:
                    if response.text:
                        
                        if response.encoding == "ISO-8859-1":
                            try:
                                result = response.text.encode("ISO-8859-1").decode("utf-8")
                            except Exception as e:
                                current_app.logger.info("uncode error", e)
                                return None
                        else:
                            result = response.text
                        return result
                    else:
                        current_app.logger.info("cookie过期，数据返回为空")
                        return None
                else:
                    self.retry -= 1
                
                    
            except Exception as e:
                # print("error", e)
                self.retry -= 1
                # return None                   