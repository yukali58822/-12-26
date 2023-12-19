import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask,render_template,request,make_response, jsonify #透過request抓前端的值
from datetime import datetime, timezone, timedelta


import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
# 靜態網頁
@app.route('/')
def index():
    homepage = "<br><a href=/webhook3>1</a><br>"
    return homepage

@app.route("/webhook3", methods=["POST"])
def webhook3():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    #msg =  req.get("queryResult").get("queryText")
    #info = "動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req.get("queryResult").get("parameters").get("rate")
        info = "我是楊子青開發的電影聊天機器人,您選擇的電影分級是：" + rate + "，相關電影：\n"

if __name__ == '__main__':
    app.run(debug=True)