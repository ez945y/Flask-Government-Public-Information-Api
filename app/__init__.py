# -- coding: utf-8 -- 
from flask import Flask, jsonify, make_response
from flask_apscheduler import APScheduler
from flask_cors import CORS
import requests
import urllib.request
from bs4 import BeautifulSoup
from pprint import pprint
from collections import defaultdict
import json
import sqlite3
from .config import Config
from .db import *
from .api import api_bp

def create_app(test_config=None ):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.register_blueprint(api_bp)

    return app


scheduler = APScheduler()

@scheduler.task('interval', id='do_job_1', seconds=10, misfire_grace_time=900)
def Updateincident():
    db = sqlite3.connect("app/db/sqlite.db")
    db.text_factory = str
    cursor = db.cursor()
    url = 'https://road.ioi.tw/?t=t1'
    page = urllib.request.urlopen(url)
    res = []
    soup = BeautifulSoup(page.read(), "html.parser")
    txt = soup.findAll('p', {'class' : 'card-text'})
    cl_value = ["badge badge-pill badge-danger",
        "badge badge-pill badge-success",
        "uptime badge badge-pill badge-secondary",
        "happentime badge badge-pill badge-secondary",
        "infosrc badge badge-pill badge-secondary",
        "area badge badge-pill badge-secondary"]
    cursor.execute("DROP TABLE IF EXISTS Incident")
    cursor.execute("CREATE TABLE Incident(type, solved, edited_time, raise_time, auth, part, title)")

    for idx, over in enumerate( soup.findAll('div', {'class' : 'card-img-overlay'})):
        new = []
        for i in range(6):
            try:
                a = over.find("span", {"class":cl_value[i]}).text
            except:
                a = None
            new.append(a if  a is not None else "nxx")
                
        new.append(txt[idx].text.replace("\n","") if txt[idx].text is not None else "nxx")

        res.append(new)
    cursor.executemany("INSERT INTO Incident VALUES(?, ?, ?, ?, ?, ?, ?)", res)
    db.commit()


        