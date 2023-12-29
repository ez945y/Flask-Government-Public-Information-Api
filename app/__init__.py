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
from flask_restful import Resource, Api, reqparse

def create_app(test_config=None ):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.register_blueprint(api_bp)
    api = Api(app)
    api.add_resource(MessageList, '/messageList')
    api.add_resource(Message, '/message/<int:message_id>')
    api.add_resource(NewMessage, '/newMessage')
    
    return app


scheduler = APScheduler()

@scheduler.task('interval', id='do_job_1', seconds=10, misfire_grace_time=900)
def Updateincident():
    with sqlite3.connect("app/db/sqlite.db") as db:
        db.text_factory = str
        cursor = db.cursor()
        try:
            page = urllib.request.urlopen("https://road.ioi.tw/?t=t1")
        except:
            page = urllib.request.urlopen('https://road.ioi.tw/?t=t1')
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

def get_db_connection():
    conn = sqlite3.connect('app/db/sqlite.db')
    conn.row_factory = sqlite3.Row
    return conn

class MessageList(Resource):
    def get(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM Messages ORDER BY Time DESC"
        messages = cursor.execute(query).fetchall()

        conn.close()

        # 將每條留言轉換為字典並構建列表
        message_list = []
        for message in messages:
            message_dict = {
                'id': message['ID'],
                'city': message['City'],
                'road': message['Road'],
                'author': message['Author'],
                'message': message['Message'],
                'time': message['Time']
            }
            message_list.append(message_dict)

        # 直接返回包含留言字典的列表
        return message_list

class Message(Resource):
    def get(self, message_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM Messages WHERE ID = ?"
        message = cursor.execute(query, (message_id,)).fetchone()

        conn.close()

        if message:
            return {'message': dict(message)}
        else:
            return {'message': None}, 404

    def put(self, message_id):
        parser = reqparse.RequestParser()
        parser.add_argument('city', required=True)
        parser.add_argument('road', required=True)
        parser.add_argument('author', required=True)
        parser.add_argument('message', required=True)
        parser.add_argument('time', required=True)
        args = parser.parse_args()

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "UPDATE Messages SET City = ?, Road = ?, Author = ?, Message = ?, Time = ? WHERE ID = ?"
        cursor.execute(query, (args['city'], args['road'], args['author'], args['message'], args['time'], message_id))
        conn.commit()

        conn.close()

        return {'message': 'Message updated successfully.'}

    def delete(self, message_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "DELETE FROM Messages WHERE ID = ?"
        cursor.execute(query, (message_id,))
        conn.commit()

        conn.close()

        return {'message': 'Message deleted successfully.'}


class NewMessage(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('city', required=True)
        parser.add_argument('road', required=True)
        parser.add_argument('author', required=True)
        parser.add_argument('message', required=True)
        parser.add_argument('time', required=True)
        args = parser.parse_args()
        print(args)
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO Messages (City, Road, Author, Message, Time) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (args['city'], args['road'], args['author'], args['message'], args['time']))
        conn.commit()

        conn.close()

        return {'message': 'Message created successfully.'}, 201