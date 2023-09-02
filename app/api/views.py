# -- coding: utf-8 -- 
from flask import Flask, jsonify, make_response
from collections import defaultdict
import requests
import json
import re
import sqlite3
from . import api_bp
from .comm import *
from app.db import *


@api_bp.route("/city")
def city():
    url_City = 'https://tdx.transportdata.tw/api/basic/v2/Basic/City?%24format=JSON'
    db = sqlite3.connect('app/db/sqlite.db')
    #db.text_factory = str
    cursor = db.cursor()
    try:
        data_response = getData(url_City)
        data_dic = json.loads(data_response.text)
        createTableCity(cursor)
        res = organizeInfoCity(data_dic)
        insertCity(cursor,res)
        db.commit()
        value_list = selectCity(cursor)
        db.close()
        key_list = ['CityID', 'CityName', 'CityCode',
                  'City', 'CountryID', 'Version']
        view = []
        for item in value_list:
            view.append(dict(zip(key_list, item)))
        print(value_list[0][1])
        return make_response(jsonify(view))
        #return json.dumps(view,ensure_ascii = False)
    except Exception as e:
        print(e)
        return {"code":404}


@api_bp.route("/cityRoad/<roadname>")
def cityRoad(roadname):
    url_City = 'https://tdx.transportdata.tw/api/basic/v2/Basic/City?%24format=JSON'
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    value_list = cursor.execute(f"SELECT DISTINCT RoadID, RoadName FROM CityRoad where RoadName like '{roadname}%' AND substr(RoadID,7,1) = 'A'  ").fetchall()
    data = [{'RoadId':i[0],"RoadName" : i[1]} for i in value_list]
    try:
        db.close()
        return json.dumps(data, ensure_ascii = False)
    except Exception as e:
        print(e)
        return {"code":404}

@api_bp.route("/citySpeed/<roadid>")
def citySpeed(roadid):
    try:
        url_CityR = f"https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/City/Taipei?%24select=VDID&%24filter=RoadID%20eq%20%27{roadid}%27&%24top=30&%24format=JSON"
        data_response = getData(url_CityR)
        data_dic = json.loads(data_response.text)
        VDIDS = [i['VDID'] for i in data_dic['VDs']]
        res = defaultdict(list)
        for VDID in VDIDS:
            url_CityR = f"https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/Taipei/{VDID}?%24top=30&%24format=JSON"
            data_response = getData(url_CityR)
            data_dic = json.loads(data_response.text)['VDLives']
            for link in data_dic:
                for linkFlow in link['LinkFlows']:
                    linkid = linkFlow['LinkID']
                    url_link = f"https://tdx.transportdata.tw/api/basic/v2/Road/Link/LinkID/{linkid}?%24format=JSON"
                    data_response = getData(url_link)
                    for lane in linkFlow['Lanes']:
                        if lane['Speed'] != '-99' and lane['Speed'] != '0.0':
                            volume = 0
                            for v in lane['Vehicles']:
                                volume += v['Volume']
                            res[json.loads(data_response.text)[0]["RoadDirection"]].append((lane['Speed'],volume))
        res_lis = []
        for key, value in res.items():
            speed, vol = 0, 0
            for tu in value:
                speed += tu[0]
                vol += tu[1]
            res_lis.append({'Direction':key,'AvgSpeed':speed / len(value)  , 'Volume':vol})
        return jsonify(res_lis)
    except Exception as e:
        print(e)
        return {"code":404}
    
@api_bp.route("/serverspot")
def serverspot():
    url_Serverspot = 'https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingServiceTime/Road/Freeway/ServiceArea?%24top=30&%24format=JSON'
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    try:
        data_response = getData(url_Serverspot)
        data_dic = json.loads(data_response.text)
        createTableServerspot(cursor)
        res = organizeInfoServerspot(data_dic)
        insertServerspot(cursor,res)
        db.commit()
        view = selectServerspot(cursor)
        db.close()
        return json.dumps(view, ensure_ascii=False)
    except Exception as e:
        print(e)
        return {"code":404}
    
@api_bp.route("/incident")
def Incident():
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    try:
        print("1")
        value_list = cursor.execute("SELECT * FROM Incident").fetchall()
        print("1")
        key_list = ["type", "solved", "edited_time", "raise_time", "auth", "part", "title"]
        view = []
        for item in value_list:
            view.append(dict(zip(key_list, item)))
        #return make_response(jsonify(view))
        db.close()
        return json.dumps(view, indent=4, ensure_ascii=False)
    except:
        return {"code":"404"}
            
@api_bp.route("/parking")
def Parking():
    url_parking = 'https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingEntranceExit/City/Taipei?format=JSON'
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    try:
        data_response = getData(url_parking)
        data_dic = json.loads(data_response.text)['ParkingEntranceExits']
        value_list = organizeInfoParking(data_dic)
        key_list = ["CarParkName", "PositionLat", "PositionLon"]
        view = []
        for item in value_list:
            view.append(dict(zip(key_list, item)))
        db.close()
        return json.dumps(view, ensure_ascii = False)
    except Exception as e:
        print(e)
        return {"code":404}

@api_bp.route("/pp")
def pp():
    return {"code":404}
@api_bp.route("/oil")
def oil():
    url= "https://www.cpc.com.tw/historyprice.aspx?n=2890"
    resp = requests.get(url)
    m = re.search("var pieSeries = (.*);", resp.text)
    jsonstr = m.group(0).strip('var pieSeries = ').strip(";")
    j = json.loads(jsonstr)
    #print(j)

    mdic = defaultdict(list)
    for record in reversed(j):
        mdic[record["name"]].append({record["data"][0]['name']:record["data"][0]['y']})

    res = []
    for k, v in mdic.items():
        res.append({"date":k, "92":v[0]['92 無鉛汽油'],  "95":v[1]['95 無鉛汽油'],  "98":v[2]['98 無鉛汽油'],  "super":v[3]['超級/高級柴油'],})

    #print(mdic)
    print(res)
    return json.dumps(res, indent=4, ensure_ascii=False)



