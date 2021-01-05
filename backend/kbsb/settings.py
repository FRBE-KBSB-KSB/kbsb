# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2020

import os
import logging

API_BASE_URL = '/api'

FILESTORE = 'fs'

LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(asctime)s - %(name)s - %(message)s',
        },
        'color': {
            'format': '%(log_color)s%(levelname)s%(reset)s: %(asctime)s %(bold)s%(name)s%(reset)s %(message)s',
            '()': 'kbsb.util.colorlogfactory.cf',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler', 
            'level': 'INFO',
            'formatter': 'color',
            # 'formatter': 'simple',
            'stream': 'ext://sys.stderr'
        }
    },
    'loggers': {
        'kbsb': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,            
        },
        'reddevil': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,            
        },
        'fastapi': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,            
        },
        'uvicorn': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,            
        },
    }
}

EXTRASALT = 'Zugzwang'


# login details
GOOGLE_CLIENT_ID = '767432590119-itkr36suu2qn41irsf5ie3mekfqdgt1q.apps.googleusercontent.com'
GOOGLE_LOGIN_DOMAINS = ['frbe-kbsb-ksb.be']

# email details
EMAIL= {
  'backend': 'SMTP',
  'host': 'localhost',
  'port': '1025',
  'sender': 'ruben.decrop@frbe-kbsb-ksb.be',
}


MONGO_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'kbsb'

TOKEN = {
    "timeout":  180,    # timeout in minutes
    "secret": "Pakjezakjemaggoan",
    "algorithm": "HS256",
    "nocheck": True,
}

MYSQL_URL = "mysql+pymysql://esyy_frbekbsbDad:Fouine17@esyy.myd.infomaniak.com/esyy_frbekbsbbe"

from local_settings import *
log = logging.getLogger('kbsb')

try:
    log.info('local settings loaded')
except ImportError:
    log.info('No local settings found')
