# -- coding: utf-8 -- 
import pandas as pd
import sqlite3

# db = sqlite3.connect('sqlite.db')
# db.text_factory = str
# cursor = db.cursor()
# cursor.execute("DROP TABLE IF EXISTS CityRoad")
# cursor.execute("CREATE TABLE CityRoad('RoadID', 'RoadName', 'CountyID', 'TownName', 'RoadClass', 'RoadClassName', 'Version', 'UpdateDate')")

# data = pd.read_csv("city_road.csv", encoding= 'utf-8') #data[:].values.tolist()
# print(data.columns.tolist())
# print(data[:].values.tolist()[0])
# cursor.executemany("INSERT INTO CityRoad VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data[:].values.tolist())
# db.commit()
# cursor.close
# db.close

db = sqlite3.connect('sqlite.db')
db.text_factory = str
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS SpeedCamera")
cursor.execute("CREATE TABLE SpeedCamera('RoadID', 'Function', 'Road', 'Introduction', 'Session', 'Direction', 'Limit', 'Latitude',Longitude)")

data = pd.read_csv("speed_camera.csv", encoding= 'utf-8') #data[:].values.tolist()
print(data.columns.tolist())
print(data[:].values.tolist()[0])
cursor.executemany("INSERT INTO SpeedCamera VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", data[:].values.tolist())
db.commit()
cursor.close
db.close