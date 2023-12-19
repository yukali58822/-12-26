import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask,render_template,request #透過request抓前端的值
from datetime import datetime, timezone, timedelta


import requests
from bs4 import BeautifulSoup

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
    homepage += "<br><a href=/books>精選圖書列表</a><br>"
    homepage += "<br><a href=/query>書名查詢</a><br>"
    homepage += "<br><a href=/spider>爬取網頁資訊</a><br>"
    homepage += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<br><a href=/searchQ>查詢開眼電影即將上映影片</a><br>"
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

@app.route("/books")
def books():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("圖書精選")
    docs = collection_ref.get()
    for doc in docs:
        bk = doc.to_dict()
        Result += "<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
        Result += "作者：" + bk["author"] + "<br>"
        Result += "週年：" + str(bk["anniversary"]) +"<br><br>"
        Result += "<img src=" + bk["cover"]+ "> </img><br><br>"
    return Result

@app.route("/query",methods=["GET","POST"])
def query():
    if request.method == "POST":
        keyword = request.form["keyword"]
        result = "您輸入的關鍵字是：" + keyword

        Result = ""
        db = firestore.client()
        collection_ref = db.collection("圖書精選")
        docs = collection_ref.get()
        for doc in docs:
            bk = doc.to_dict()
            if keyword in bk["title"]:
                Result += "<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
                Result += "作者：" + bk["author"] + "<br>"
                Result += "週年：" + str(bk["anniversary"]) + "<br><br>"
                Result += "<img src=" + bk["cover"] + "> </img><br><br>"
        return Result

    else:
        return render_template("ex1.html")

@app.route("/spider")
def spider():
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    # print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")

    results = sp.select(".team-box")  # 取多筆
    Result = ''
    for result in results:
        Result += "<a href=" + result.find('a').get('href') + ">" + result.text + "</a><br>"
        Result += result.find('a').get('href') + "<br>" + "<br>"  # 取一筆
    return Result

@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        hyperlink = "<a href=" + hyperlink + ">" + hyperlink + "</a><br>"
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
          }

        db = firestore.client()
        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)

    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate



@app.route("/searchQ", methods=["POST","GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]:
                info += "片名：" + doc.to_dict()["title"] + "<br>"
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>"
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"
        return info
    else:
        return render_template("input.html")


if __name__ == '__main__':
    app.run(debug=True)