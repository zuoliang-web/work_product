import re
import random
import time
import json
import queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

from ..dbutils.Ckafka import CKafkaConsumer

from ..models.degree import ElasticDegree, Agg ,Suggest



def get_slide_locus(distance):
    #计算出一个滑动轨迹
    distance += 8
    v = 0
    m = 0.3
    # 保存0.3内的位移
    tracks = []
    current = 0
    mid = distance * 4 / 5
    while current <= distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        s = v0 * m + 0.5 * a * (m ** 2)
        current += s
        tracks.append(round(s))
        v = v0 + a * m
    # 由于计算机计算的误差，导致模拟人类行为时，会出现分布移动总和大于真实距离，这里就把这个差添加到tracks中，也就是最后进行一步左移。
#     print(sum(tracks))
#     tracks.append(-(sum(tracks) - distance * 0.5))
#     print(sum(tracks))
    # tracks.append(10)
    return tracks

def coverGapTouilet(url):
    
    driver = webdriver.Chrome(executable_path=r"D:\爬虫\chromedriver.exe")
    driver.get(url)
    
    
    styleText = driver.find_element(By.XPATH, "//div[@class='verify-img-panel']").get_attribute("style")
    # img_url = re.findall(r"url\(\"(.*)\"\)", styleText)[0]
    gap_info = driver.find_element(By.XPATH, "//div[@class='verify-gap']").get_attribute("style")
    gap_width = re.findall(r"width:\s(.*?)px", gap_info)[0]
    gap_height = re.findall(r"height:\s(.*?)px", gap_info)[0]
    gap_top = re.findall(r"top:\s(.*?)px", gap_info)[0]
    gap_left = re.findall(r"left:\s(.*?)px", gap_info)[0]
    move_left = int(float(gap_left))

    action = ActionChains(driver)
    # 选择拖动滑块的节点
    sli_ele = driver.find_element(By.XPATH,'//div[@class="verify-move-block"]')
    action.click_and_hold(sli_ele)
    
    locus = get_slide_locus(move_left)
    locus[-2] -= 2
    locus[-1] -= 3
    for loc in locus:
        print(loc)
        time.sleep(0.01)
        action.move_by_offset(loc, random.randint(-5, 5)).perform()
    # 第三步：释放鼠标
    action.release()
    # 执行动作
    action.perform()
    
    if "知网节超时验证" not in driver.page_source:
        return driver.page_source
    else:
        return None
    
 
class CAopceptor(object):
    
    def __init__(self):
        self.kclient = None
        self.topiclist = list()
        self.KafkaMsgQueue = queue.Queue()


    def ConnectKafka(self, groupID):
        self.kclient = CKafkaConsumer()
        if self.kclient.connect(groupID, self.topiclist):
            return True
        return False
    
    def ProcessKafkaData(self, callback=None):
        if self.kclient:
            if not callback:
                callback = self.DataProcesser
            self.kclient.SetKafkaDataProcesser(callback)
            self.kclient.run()
        else:
            return False
    
    
    def DataProcesser(self, msg):
        recv = "%s:%d:%d: key=%s value=%s" % (msg.topic, msg.partition, msg.offset, msg.key, msg.value)
        print(recv)

        x = json.loads(msg.value)

        self.KafkaMsgQueue.put(x)
        time.sleep(5)
        return
    
    
    
    def InsertElasticKafka(self):
        
        print("进入到kafka检测区")
        while True:

            while not self.KafkaMsgQueue.empty():  # for each tag ,quey  tool node

                nmapLis = self.KafkaMsgQueue.get()
                
                print("x", nmapLis)
                for scansj in nmapLis:
                    
                    print("数据 录入到 elastic 中", scansj)
                    

            time.sleep(2)
            
    def setTopic(self, topicname):
        self.topiclist.append(topicname)
        return
           