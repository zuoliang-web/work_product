# -*- coding: utf-8 -*-
 
from datetime import timedelta
from celery.schedules import crontab
from . import conf
 
# Broker and Backend
BROKER_URL = 'redis://%s:%s' % (conf.get("redis", "host"), conf.get("redis", "port"))
CELERY_RESULT_BACKEND = 'redis://%s:%s/%s'  % (conf.get("redis", "host"), conf.get("redis", "port"), conf.get("redis", "db"))
BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_EXPIRES= 15
# Timezone
CELERY_TIMEZONE='Asia/Shanghai'    # 指定时区，不指定默认为 'UTC'
# CELERY_TIMEZONE='UTC'
 
# import
CELERY_IMPORTS = (
    'apps.spiderTask.view',
 
)
 
# schedules
CELERYBEAT_SCHEDULE = {
    'cn_finace': {
         'task': 'apps.spiderTask.view.press_cn',
         'schedule': timedelta(hours=1),       # 每 30 秒执行一次
        #  'args': (5, 8)                           # 任务函数参数
    },
    'sina_finace': {
         'task': 'apps.spiderTask.view.press_sina',
         'schedule': timedelta(hours=1),       # 每 30 秒执行一次
        #  'args': (5, 8)                           # 任务函数参数
    },
    'wy_finace': {
         'task': 'apps.spiderTask.view.press_wy',
         'schedule': timedelta(hours=1),       # 每 30 秒执行一次
        #  'args': (5, 8)                           # 任务函数参数
    },
    'tx_finace': {
         'task': 'apps.spiderTask.view.press_tx',
         'schedule': timedelta(hours=1),       # 每 30 秒执行一次
        #  'args': (5, 8)                           # 任务函数参数
    },
    'cns_finace': {
         'task': 'apps.spiderTask.view.press_cns',
         'schedule': timedelta(hours=1),       # 每 30 秒执行一次
        #  'args': (5, 8)                           # 任务函数参数
    },
    # 'multiply-at-some-time': {
    #     'task': 'celery_app.task2.multiply',
    #     'schedule': crontab(hour=9, minute=50),   # 每天早上 9 点 50 分执行一次
    #     'args': (3, 7)                            # 任务函数参数
    # }
}




# bear      celery -A apps beat
# worker    celery -A apps worker --loglevel=info -P eventlet  -c 20
