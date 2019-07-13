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
listen = False
redisCheckThread = None

@app.route('/Selector/Start',methods=['POST'])
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
        while listen:
            data = r.lpop(configDef['subscribeOn'])
            if data is not None:
                dataDic = json.loads(data.decode("utf-8"))
                barLst = dataDic["Bars"]
                last = dataDic["Last"]
                #print("Bars: " + str(barLst))
                start = time.time()
                startIdx = Helper.searchTemplate(lst, len(barLst))
                end = time.time()
                print(str(end-start))
                barsTempRelated = {
                    "bars": barLst,
                    "templates": startIdx,
                    "Last": last
                }
                r.rpush(configDef['publishOn'], json.dumps(barsTempRelated))

if __name__ == '__main__':
    global configDef
    config = configparser.ConfigParser()
    config.read('config.ini')
    configDef = config['DEFAULT']
    r.delete(configDef['publishOn'])
    app.config['SERVER_NAME'] = os.getenv("Selector_HOST")
    StartListen()
    app.run(debug=False)
