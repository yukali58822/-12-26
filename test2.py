import requests
from fake_useragent import UserAgent
import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


for page in range(45):# 走訪0~9頁。
    url = f'https://api.hahow.in/api/courses?limit=24&page={page}'
    headers = {'User-agent':UserAgent().random}
    response = requests.get(url,headers=headers)
    data = response.json()# json格式字串轉python。
    print(data)

    for course in data['data']:
        title = course['title']
        owner_name = course['owner']['name']
        price = course['price']
        student_number = course['numSoldTickets']

    doc = {
        "title": title,
        "owner_name": owner_name,
        "price": price,
        "student_number": student_number
    }

    db = firestore.client()
    doc_ref = db.collection("課程").document()
    doc_ref.set(doc)
