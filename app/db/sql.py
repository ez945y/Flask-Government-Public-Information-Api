# -- coding: utf-8 -- 
from flask import Flask,jsonify
import requests
from pprint import pprint
import json
import sqlite3
def selectServerspot(cursor):
    lis = cursor.execute("SELECT * FROM Serverspot").fetchall()
    if(len(lis)!=0):
        return lis
    
def organizeInfoServerspot(data_dic):
    res = list()
    data_dic = data_dic["ServiceTimes"]
    for d in data_dic:
        lis = []
        d_lis = list(d.values())
        lis.append(d_lis[0])
        lis.append(d_lis[1]["Zh_tw"])
        lis2 = list()
        for day in list(d_lis[2][0]["ServiceDay"].values())[1:]:
            lis2.append(day)
        lis.extend(lis2)
        lis.extend(d_lis[2][1:5])
        for idx, m in enumerate(lis[2:]):
            lis[idx+2] = bool(m)
        print(lis)
        res.append(lis)
    return res
    

def insertServerspot(cursor,res):
    cursor.executemany("INSERT INTO Serverspot VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", res)
        
def createTableServerspot(cursor):
    cursor.execute("DROP TABLE IF EXISTS Serverspot")
    cursor.execute("""CREATE TABLE Serverspot(ServerspotId, ServerSpotName, Monday, 
        Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday,NationalHoliday)""")

#-----------------------------------------------------------------------------------------------------------------------

def selectTourism(cursor):
    lis = cursor.execute("SELECT * FROM Tourism").fetchall()
    if(len(lis)!=0):
        return lis
    
def organizeInfoTourism(data_dic):
    res = list()
    #這裡僅整理前8筆
    for d in data_dic[:8]:
        data_list_Tourism = list(d.values())
        i = 1 if list(d.keys())[6] == "OpenTime" else 0
        lis = data_list_Tourism[:8-i]
        if(i==1):lis.append("Without TravelInfo")
        lis.extend(list(data_list_Tourism[8-i].values()))
        print(data_list_Tourism[9-i])
        lis.extend(list(data_list_Tourism[9-i].values()))
        lis.extend(data_list_Tourism[11-i:])
        res.append(lis)
    return res

def insertTourism(cursor,res):
    cursor.executemany("INSERT INTO Tourism VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)", res)
        
def createTableTourism(cursor):
    cursor.execute("DROP TABLE IF EXISTS Tourism")
    cursor.execute("""CREATE TABLE Tourism(ScenicSpotID, ScenicSpotName, DescriptionDetail, 
        Description, Phone, Address, TravelInfo, OpenTime, PictureUrl1,PictureDescription1,
         PositionLon,PositionLat,GeoHash, City, SrcUpdateTime, UpdateTime)""")
    
#----------------------------------------------------------------------------------------------------------------------

def selectCity(cursor):
    lis = cursor.execute("SELECT * FROM City").fetchall()
    if(len(lis)!=0):
        return lis

def organizeInfoCity(data_dic):
    res = list()
    for d in data_dic:
        my_string_list= [str(i) for i in list(d.values())]
        res.append(my_string_list)
    return res

def createTableCity(cursor):
    cursor.execute("DROP TABLE IF EXISTS City")
    cursor.execute("""CREATE TABLE City(CityID, CityName, CityCode, 
        City, CountryID, Version)""")
    
def insertCity(cursor,res):
    cursor.executemany("INSERT INTO City VALUES(?, ?, ?, ?, ?, ?)", res)


def organizeInfoParking(data_dic):
    res = list()
    print("start")
    for d in data_dic:
        lis = []
        if(d['CarParkName'] != ""):
            lis.append(d['CarParkName']["Zh_tw"])
        else:
            continue
        lis.append(d['EntranceExits'][0]["Position"]["PositionLat"])
        lis.append(d['EntranceExits'][0]["Position"]["PositionLon"])
        print(lis)
        res.append(lis)
    return res