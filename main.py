from sqlite3.dbapi2 import connect
from flask import Flask,render_template,request,redirect
from email.message import EmailMessage
from smtplib import SMTP
import smtplib
import sqlite3
import multiprocessing
import time
import numpy as np
from XrayScanner import XRAY
from PIL import Image
from CellScanner import CellScanner


app=Flask("BreastCancerAPP")

def algo_test(imdicts):
    dicts={"no1":[],"no2":[],"no3":[]}
    
    for key in dicts.keys():
        dicts[key]=imdicts.getlist(key)

    res=0
    coef={"no1":15,"no2":30,"no3":22}
    for key in dicts.keys():
        res+=coef[key]*len(dicts[key])
    return res


def send_email(email):
    content=""
    with open("templates/email_template.html","r") as file:
        content+=file.read()

    email = EmailMessage()
    email['Subject'] = 'Breast Cancer Awareness'
    email['From'] = 'BCA'
    email['To'] = email
    email.set_content(content, subtype='html')

    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.starttls()
        s.login('email', 'pass')  # EMAIL AND PASSWORD FOR SERVER EMAIL HERE !
        s.send_message(email)
    print("SENT!!!!!!!!!!")
    

def connect_db():
    name="emails.db"
    conn=sqlite3.connect(name)
    cursor = conn.execute("SELECT email from users;")
    for row in cursor:
        print(row[0])
        send_email(row[0])
    cursor.close()


@app.route("/results",methods=["GET","POST"])
def results():

    if(request.method=="GET"):
        return redirect("index_page")
    result=algo_test(request.form)
    if(result<30):
        return render_template("results.html",details={"img":"firstaidg.png","msg":"Overall result is okay but do not forget to check up every month.Early detection and identification of cancer is very crucial."})
    if(result>=30 and result<=50):
        return render_template("results.html",details={"img":"firstaidy.png","msg":"Doctor examination highly recommended.Results claim that you may have lumps ,benign or cyst. "})
    if(result>50):
        return render_template("results.html",details={"img":"firstaid.png","msg":"Immediate action required ! It looks like you might have malignant,cancerous tissue or cyst. "})
    


@app.route("/xray",methods=["GET","POST"])
def xray():
    if(request.method=="POST"):
        img=Image.open(request.files['image'].stream)
        rgbimg = Image.new("RGB", img.size)
        rgbimg.paste(img)
        abc=XRAY()
        res=abc.forward(rgbimg)
        return render_template("results2.html",details={"img":"res.png","msg":f"Xray image identified as {res}. Right side you can see estimated heatmap for given xray image.Red color indicates high likely cancerous tissue,lump or cyst while blue indicates less likely tissue."})
        
    return render_template("xray.html")



@app.route("/cell",methods=["GET","POST"])
def cell():
    if(request.method=="POST"):
        img=Image.open(request.files['image'].stream)
        rgbimg = Image.new("RGB", img.size)
        rgbimg.paste(img)
        abc=CellScanner()
        res=abc.forward(rgbimg)
        res='Positive' if(res==1) else 'Negative'
        return render_template("results.html",details={"img":"cell.png","msg":f"Cell image identified as {res}."})
        
    return render_template("cell.html")








@app.route("/email",methods=["GET","POST"])
def email_page():
    if(request.method=="GET"):
        return render_template("email.html")
    else:
        email=request.form["email"]
        name="emails.db"
        conn=sqlite3.connect(name)
        cursor = conn.execute(f"insert into users(email) values('{email}');")
        conn.commit()
        cursor.close()
        return render_template("email.html")



@app.route("/")
def index_page():
    return render_template("index.html")


@app.route("/selfexam",methods=["GET"])
def self_exam():
    return render_template("selfexam.html")
    

def server_runner():
    app.run()

def email_sender_server():
    time.sleep(60*60*24*7)  # for weekly tips first wait 1 week  send
    connect_db()


if(__name__=="__main__"):

    service = multiprocessing.Process(name='email_sender', target=email_sender_server)
    worker_1 = multiprocessing.Process(name='web_server', target=server_runner)

    worker_1.start()
 #   service.start()





