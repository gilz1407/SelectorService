import configparser
import json
import os
import threading
import time
import requests
from flask import Flask

import Helper
from RedisConnection import connect

isUp = False
lst = []
r = connect()
app = Flask(__name__)
redisCheckThread = None

#@app.route('/Selector/Start',methods=['POST'])
def StartListen():
    global redisCheckThread, listen, lst

    # load combination list from redis
    combLst = r.get("tempComb")
    l = json.loads(combLst)
    lst = eval(l['tl'])

    if redisCheckThread is None:
        listen = True
        redisCheckThread = RedisCheck()
        redisCheckThread.start()
        return "Listening started"
    else:
        return "Already listening"

class RedisCheck(threading.Thread):
    global listen
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        barsTempRelated = {
            "bars": "",
            "templates": "",
            "Last": ""
        }
        subOn = configDef['subscribeOn']
        pubOn = configDef['publishOn']
        while True:
            data = r.lpop(subOn)
            if data is not None:
                dataDic = json.loads(data.decode("utf-8"))
                barLst = dataDic["Bars"]
                print("Bars: " + str(barLst) +"Last: "+str(dataDic["Last"]))
                startIdx = 0
                if len(barLst) > 0:
                    startIdx = lengthMap[str(len(barLst))]
                startIdx = Helper.searchTemplate(lst, len(barLst))
                barsTempRelated["bars"] = barLst
                barsTempRelated["templates"] = startIdx
                barsTempRelated["Last"] = dataDic["Last"]

                if bool(dataDic["Last"]) is True or len(barLst) > 0:
                    r.rpush(pubOn, json.dumps(barsTempRelated))

if __name__ == '__main__':
    global configDef
    config = configparser.ConfigParser()
    config.read('config.ini')
    configDef = config['DEFAULT']
    r.delete(configDef['subscribeOn'])
    r.delete(configDef['publishOn'])
    lengthMap = json.loads(r.get('lengthMap'))
    app.config['SERVER_NAME'] = os.getenv("Selector_HOST")
    StartListen()
    app.run(debug=False)
