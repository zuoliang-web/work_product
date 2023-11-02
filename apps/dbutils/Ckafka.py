import kafka
from kafka import KafkaProducer, KafkaConsumer
from kafka.structs import TopicPartition 
from threading import Thread
import traceback
import json

from ..  import conf

KafkaIp = "%s:%s" % (conf.get("kafka", "serverip"), conf.get("kafka", "serverport"))

class CKafkaProducer(object):
    def __init__(self):
        self.KProducer = None
        
    def connect(self):
        
        self.KProducer = KafkaProducer(bootstrap_servers=[KafkaIp])
        if self.KProducer:
            return True
        else:
            return False    
    
    def sendMsg(self, topic, msg_dict):
             
        msg = json.dumps(msg_dict).encode()
        x = self.KProducer.send(topic, msg)
        try:
            x.get(timeout=10)
        except kafka.errors as e:
            traceback.format_exc()
            return False
        return True
    
    def disconnect(self):
        if self.KProducer:
            self.KProducer.close()
            return True
        return False
    
        
        
class CKafkaConsumer(object):
    def __init__(self):
        self.KConsumer = None   
    
    def connect(self,  GroupID,topic):
        self.KConsumer = KafkaConsumer(group_id=GroupID, bootstrap_servers=KafkaIp, auto_offset_reset="latest")
        self.KConsumer.subscribe(topic)
        
        if self.KConsumer:
            return True
        return False
    
    def assign(self, topic):
        
        if self.KConsumer:
            self.KConsumer.assign([TopicPartition(topic=topic, partition=0)])
            return True
        return False
    
    def SetKafkaDataProcesser(self,callback=None):
        self.callback=callback
        self.daemon = True

    def disconnect(self):
        if self.KConsumer:
            self.KConsumer.close()
            return True
        return False
    
    def run(self):
        for msg in self.KConsumer:
            if self.callback:
                self.callback(msg)
            print(str(msg.value, encoding='utf-8'))
            
            
    