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

@app.route('/isUp',methods=['GET'])
def isUpAndRunning():
    return ""

@app.route('/Selector/Start',methods=['POST'])
def StartListen():
    global redisCheckThread, listen, lst
    print("here")
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

@app.route('/Bulker/Stop/',methods=['POST'])
def StopListen():
    global listen
    listen = False
    return "Listening stopped"

class RedisCheck(threading.Thread):
    global listen
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while listen:
            data = r.lpop(configDef['subscribeOn'])
            if data is not None:
                s = data.decode("utf-8")
                dataDic = json.loads(s)
                barLst = dataDic["Bars"]
                print("Bars: " + str(barLst))
                startIdx = Helper.searchTemplate(lst, len(barLst))
                barsTempRelated = {
                    "bars": barLst,
                    "templates": startIdx
                }
                r.lpush(configDef['publishOn'], json.dumps(barsTempRelated))

def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            try:
                rr = requests.get("http://"+os.getenv("Selector_HOST")+"/isUp")

                if rr.status_code == 200:
                    time.sleep(2)
                    print('Server started, quiting start_loop')
                    not_started = False
                    StartListen()
                    break
                print(rr.status_code)
            except:
                print('Server not yet started')
            time.sleep(5)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()

if __name__ == '__main__':
    global configDef
    config = configparser.ConfigParser()
    config.read('config.ini')
    configDef = config['DEFAULT']
    r.delete(configDef['publishOn'])
    app.config['SERVER_NAME'] = os.getenv("Selector_HOST")
    StartListen()
    #app.run(debug=True,use_reloader=False)
    app.run(debug=False)
