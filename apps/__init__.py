from celery import Celery
import os
from configparser import ConfigParser
conf = ConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config_file = os.path.join(BASE_DIR, "mission.ini")
conf.read(config_file)
celerytask = Celery('demo')
celerytask.config_from_object('apps.celeryconfig')