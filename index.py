import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime, timezone, timedelta


app = Flask(__name__)

# 靜態網頁
@app.route('/')
def index():
    homepage = "<h1>謝佩宸的Python網頁</h1>"
    homepage+= "<a href=/mis>MIS單純傳入文字</a><br>"
    homepage+= "<a href=/today>顯示日期與時間</a><br>"
    homepage+= "<a href=/welcome?keyword=PEI>傳入使用者名稱</a><br>"
    homepage+= "<a href=/about>關於我的網頁</a><br>"
    homepage+= "<a href=/account>關於我的帳密</a><br>"
    homepage += "<br><a href=/read>人選之人─造浪者演員查詢</a><br>"

    return homepage

@app.route('/mis')
def course():
    return "<h1>資訊管理導論</h1> "

#動態網頁
@app.route('/today')
def today():
    tz = timezone(timedelta(hours=+8))
    now = datetime.now(tz)
    return render_template('today.html',datetime=str(now))

@app.route('/about')
def about():
    return render_template('javascrip.html')

@app.route('/welcome',methods=["GET","POST"])
def welcome():
    user = request.values.get('keyword')
    return render_template('welcome.html',text=user)

@app.route("/account",methods=["GET","POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form['pwd']
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd
        return result
    else:
        return render_template("account.html")
@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("人選之人─造浪者")
    docs = collection_ref.get()
    for doc in docs:
        Result += "文件內容：{}".format(doc.to_dict()) + "<br>"
    return Result

@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    msg =  req.get("queryResult").get("queryText")
    info = "動作：" + action + "； 查詢內容：" + msg
    return make_response(jsonify({"fulfillmentText": info}))

#if __name__ == '__main__':
#   app.run(debug=True)