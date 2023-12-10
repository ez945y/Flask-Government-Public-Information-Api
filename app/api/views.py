# -- coding: utf-8 -- 
from flask import Flask, jsonify, make_response
from collections import defaultdict
import requests
import urllib.request
from bs4 import BeautifulSoup
import json
import sqlite3
from . import api_bp
from .comm import *
from app.db import *
import re
from numpy import sin, cos, arccos, pi, round
from scipy.spatial import KDTree
import os

@api_bp.route("/")
def index():
    return "Hello"
    
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
        cursor.close
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
    try:
        value_list = cursor.execute(f"SELECT DISTINCT RoadID, RoadName FROM CityRoad where RoadName like '{roadname}%' AND substr(RoadID,7,1) = 'A'  ").fetchall()
        data = [{'RoadId':i[0],"RoadName" : i[1]} for i in value_list]
        cursor.close()
        db.close()
        return json.dumps(data, ensure_ascii = False)
    except Exception as e:
        print(e)
        return {"code":404}

@api_bp.route("/citySpeed/<roadid>")
def citySpeed(roadid):
    url_CityR = f"https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/City/Taipei?%24select=VDID&%24filter=RoadID%20eq%20%27{roadid}%27&%24top=30&%24format=JSON"
    try:
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
        cursor.close()
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
        cursor.close()
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
        cursor.close()
        db.close()
        return json.dumps(view, ensure_ascii = False)
    except Exception as e:
        print(e)
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

@api_bp.route("/weather")
def weather():
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization=CWB-9451F1F8-364F-48A5-AEF6-60F3ACEBC9D7'

    data = requests.get(url)   # 取得 JSON 檔案的內容為文字

    res = []
    data_json = data.json()    # 轉換成 JSON 格式
    prohibit = ["WeatherDescription","PoP12h","AT","CI","RH","WD","WS","Td"]
    for record in  data_json['records']['locations'][0]["location"]:
        mdic = {}
        mdic["locationName"] = record["locationName"]
        for w in record["weatherElement"]:
            if w["elementName"] in prohibit:continue
            for idx, p in enumerate(w["time"]):
                if idx >=4 and w["elementName"] == "PoP6h":break
                if idx >=8 and w["elementName"] == "Wx":break
                if idx >=8 and w["elementName"]=="AT":break
                if idx >=8 and w["elementName"]=="T":break
                if idx >=8 and w["elementName"]=="RH":break
                if idx >=8 and w["elementName"]=="CI":break
                if idx >=8 and w["elementName"]=="WS":break
                if idx >=8 and w["elementName"]=="WD":break
                if idx >=8 and w["elementName"]=="Td":break
                tag = w["elementName"]+str(idx+1)
                mdic[tag] = p["elementValue"][0]["value"]
                
        res.append(mdic)
    print(res[0].items())
    print(res) 
    return json.dumps(res, indent=4, ensure_ascii=False)


@api_bp.route("/cameraTest")
def CameraTest():
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    try:
        value_list = cursor.execute(f"SELECT * FROM SpeedCamera").fetchall()
        key_list = ["ID", "Type","Road","Introduction","Session","Direction","Limit","Latitude", "Longitude"]
        view = []
        for item in value_list:
            view.append(dict(zip(key_list, item)))
        cursor.close()
        db.close()
        return json.dumps(view, ensure_ascii = False)
    except Exception as e:
        print(e)
        return {"code":404}

@api_bp.route("/cameraMark")
def CameraMark():
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    try:
        value_list = cursor.execute(f"SELECT * FROM SpeedCamera").fetchall()
        key_list = ["ID", "Type","Road","Introduction","Session","Direction","Limit","Latitude", "Longitude"]
        view = []
        for item in value_list:
            view.append(dict(zip(key_list, item)))
        cursor.close()
        db.close()
        return json.dumps(view, ensure_ascii = False)
    except Exception as e:
        print(e)
        return {"code":404}

@api_bp.route("/weatherLocation/<latitude>,<logitude>")
def weatherLocation(latitude,logitude):
    token = os.getenv("GoogleToken")
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{logitude}&key={token}&language=zh-TW'

    data = requests.get(url)   # 取得 JSON 檔案的內容為文字
    data_json = data.json()
    res = data_json['results'][0]['address_components'][3]['short_name']
    return json.dumps({'district':res}, indent=4, ensure_ascii=False)

@api_bp.route("/RoadShoulder")
def RoadShoulder():
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    weekday = datetime.today().weekday()
    try:
        if(weekday != 6 & weekday != 7):
            if(weekday == 5):
                lis = cursor.execute("""select Route,RoadSection,Milage,"Opentimes1(Weekday)","Opentimes2(Weekday)","Opentimes(Fridayonly)",SpeedLimit from RoadShoulder where "Opentimes1(Weekday)" IS NOT NULL OR "Opentimes2(Weekday)" IS NOT NULL OR "Opentimes(Fridayonly)" IS NOT NULL""").fetchall()
                key_list = ["Route","RoadSection","RoadSection","Milage","Opentimes1(Weekday)","Opentimes2(Weekday)","Opentimes(Fridayonly)","SpeedLimit"]
                list = []
                for item in lis:
                    list.append(dict(zip(key_list,item)))
            else:
                lis = cursor.execute("""select Route,RoadSection,Milage,"Opentimes1(Weekday)","Opentimes2(Weekday)" ,SpeedLimit from RoadShoulder where "Opentimes1(Weekday)" IS NOT NULL OR "Opentimes2(Weekday)" IS NOT NULL""").fetchall()
                key_list = ["Route","RoadSection","RoadSection","Milage","Opentimes1(Weekday)","Opentimes2(Weekday)","SpeedLimit"]
                list = []
                for item in lis:
                    list.append(dict(zip(key_list,item)))
        else:
            lis = cursor.execute("""select Route,RoadSection,Milage,"Opentimes1(Weekend)","Opentimes2(Weekend)",SpeedLimit from RoadShoulder where "Opentimes1(Weekend)" IS NOT NULL OR "Opentimes2(Weekend)" IS NOT NULL""").fetchall()
            key_list = ["Route","RoadSection","RoadSection","Milage","Opentimes1(Weekend)","Opentimes2(Weekend)","SpeedLimit"]
            list = []
            for item in lis:
                list.append(dict(zip(key_list,item)))
        cursor.close()
        db.close()
        print(lis)
        return json.dumps(list, ensure_ascii = False)
    except Exception as e:
        print(e)
        return{"code":404}

@api_bp.route("/oilStation")
def oilStation():
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    try:
        value_list = cursor.execute("select * from OilStation").fetchall()
        key_list = ["Station", "Address","Longitude","Latitude" ]
        view = []
        for item in value_list:
            view.append(dict(zip(key_list, item)))
        cursor.close()
        db.close()
        return json.dumps(view, ensure_ascii = False)
    except Exception as e:
        print(e)
        return {"code":404}

@api_bp.route("/cctv")
def cctv():
    res = []
    direct = ['songshan','xinyi','daan','zhongshan','zhongzheng','datong','wanhua','wenshan','nangang','neihu','shilin','beitou']
    for sector in direct:
        url = f"https://tw.live/city/taipeicity/{sector}/"
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        request = urllib.request.Request(url = url, headers = headers, method = 'GET')

        response = urllib.request.urlopen(request)

        content = response.read()

        soup = BeautifulSoup(content, "html.parser")
        txt = soup.findAll('div', {'class' : 'cctv-stack'})
        for t in txt:
            res.append(t.find('p').text)
    return res

def rad2deg(radians):
    degrees = radians * 180 / pi
    return degrees

def deg2rad(degrees):
    radians = degrees * pi / 180
    return radians

def getDistanceBetweenPointsNew(latitude1, longitude1, latitude2, longitude2, unit = 'kilometers'):
    
    theta = longitude1 - longitude2
    print(longitude1)
    print(longitude2)
    distance = 60 * 1.1515 * rad2deg(
        arccos(
            (sin(deg2rad(latitude1)) * sin(deg2rad(latitude2))) + 
            (cos(deg2rad(latitude1)) * cos(deg2rad(latitude2)) * cos(deg2rad(theta)))
        )
    )
    
    if unit == 'miles':
        return round(distance, 2)
    if unit == 'kilometers':
        return round(distance * 1.609344, 2)

class CAMERA:
    def __init__(self, ID, latitude, longitude):
        self.ID = ID
        self.latitude = latitude
        self.longitude = longitude

def fetch_camera_data():
    db = sqlite3.connect('app/db/sqlite.db')
    cursor = db.cursor()
    query = "SELECT ROADID, latitude, longitude from SpeedCamera"
    cursor.execute(query)
    camera_data = cursor.fetchall()
    cameras = []

    for data in camera_data:
        camera = CAMERA(data[0], data[1], data[2])
        cameras.append(camera)

    db.close()
    return cameras

@api_bp.route("/findCamera/<float:latitude>,<float:longitude>")
def findCamera(latitude, longitude):

    camera_data = fetch_camera_data()
    coordinates = [(camera.longitude, camera.latitude) for camera in camera_data]
    kdtree = KDTree(coordinates)
    nearest_distance, nearest_camera_index = kdtree.query((longitude, latitude))
    nearest_camera = camera_data[nearest_camera_index]
    distance = getDistanceBetweenPointsNew(latitude, longitude,float(nearest_camera.latitude),float(nearest_camera.longitude)) * 1000
    if(distance>0.0 and distance <= 300 and (abs(latitude-latitude )<0.0005 or abs(longitude-longitude)<0.0005)):
        with sqlite3.connect('app/db/sqlite.db') as db:
            cursor = db.cursor()
            cid = nearest_camera.ID
            query = f"SELECT * from SpeedCamera WHERE ROADID = '{cid}'"
            c = cursor.execute(query).fetchone()
            value_list = list(c)
            value_list.append(distance)
            print(value_list)
        key_list = ["ID", "Type","Road","Introduction","Session","Direction","Limit","Latitude", "Longitude","Distance"]
        return dict(zip(key_list, value_list))
    else:
        return {"ID":"0", "Type":"0","Road":"0","Introduction":"0","Session":"0","Direction":"0","Limit":"0","Latitude":"0.0", "Longitude":"0.0","Distance":1000}