import configparser
import json
import os
import threading
import time
import requests
from flask import Flask
import Helper
#sys.path.append(os.path.abspath('../CrossInfra'))
from RedisConnection import connect

lst = []
r = connect()
app = Flask(__name__)
listen = False
redisCheckThread = None

@app.route('/Selector/Start',methods=['POST'])
@app.before_first_request
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

def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            try:
                rr = requests.get("http://"+configDef['url'])
                if rr.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(rr.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


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
                f = int(dataDic["from"])
                t = int(dataDic["To"])
                print("Bars: " + str(barLst) + " From: "+str(f) + " To: "+str(t))
                relevantTemplates = Helper.searchTemplate(lst, t+1)
                barsTempRelated={
                    "bars": barLst,
                    "templates": relevantTemplates
                }
                r.lpush(configDef['publishOn'], json.dumps(barsTempRelated))

if __name__ == '__main__':
    global configDef
    config = configparser.ConfigParser()
    config.read('config.ini')
    configDef = config['DEFAULT']
    app.config['SERVER_NAME'] = os.getenv("Selector_HOST")
    start_runner()
    app.run(debug=True)
