import configparser
import json
import os
import sys
import threading
from flask import Flask, request
sys.path.append(os.path.abspath('../CrossInfra'))
from Combination import Combination
from RedisManager import connect
from BasicFunc import BasicFunc


lst = []
r = connect()
app = Flask(__name__)
listen = False
redisCheckThread = None
@app.route('/Selector/Start',methods=['POST'])
def StartListen():
    global redisCheckThread,listen,lst
    comb = Combination()
    comb.InitCombinations()
    lst = comb.GetCombinationLst()
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
            data = r.lpop('TemplateList')
            if data is not None:
                s = data.decode("utf-8")
                dataDic = json.loads(s)
                barLst = dataDic["Bars"]
                f = int(dataDic["from"])
                t = int(dataDic["To"])
                print("Bars: " + str(barLst) + " From: "+str(f) + " To: "+str(t))
                relevantTemplates = BasicFunc.findTemplates(lst, t+1)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    configDef = config['DEFAULT']
    app.config['SERVER_NAME'] = configDef['url']
    app.run(debug=True)
