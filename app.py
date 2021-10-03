import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, g, flash
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import folium 
import json
import sqlite3
import db

app = Flask(__name__)
###DB###
app.config.from_object(__name__)
 
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, './db/db4.sqlite3'),
    SECRET_KEY='foo-baa',
))

def connect_db():
    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
###DB###    

ICON_DIR = "img/weather_icon"
SAVE_DIR = "img"
CACHE_DIR = "cache_file"

if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)

@app.route('/img/<path:filepath>')
def register_folder(filepath):
    return send_from_directory(SAVE_DIR, filepath)

#キャッシュ用フォルダの読み込み
if not os.path.isdir(CACHE_DIR):
    os.mkdir(CACHE_DIR)

@app.route('/cache_file/<path:filepath>')
def avoid_cache(filepath):
    return send_from_directory(CACHE_DIR, filepath)

today = (datetime.now().strftime('%a %d %B'))

url = 'https://api.openweathermap.org/data/2.5/weather'
api_key = "XXXX" #my key
city_id = '2147714' # Sydney
params = {"id": city_id, "appid" : api_key, 'lang': 'en', 'units':'metric'}
res = requests.get(url, params=params)
data = json.loads(res.text)

location = data['name']
weather = data['weather'][0]['description']
temperature = int(data['main']['temp'])
"""temp_max = data["main"]["temp_max"]"""
icon = data['weather'][0]['icon']

filepath = './img/weather_icon/' + icon + '.png'

#icon表示
if not os.path.isdir(ICON_DIR):
        os.mkdir(ICON_DIR)
@app.route('/img/weather_icon/<path:filepath>')
def display_icon(filepath):
    return send_from_directory(ICON_DIR, filepath)

#weather表示
@app.route("/", methods=["GET","POST"])
def main():
    if request.method == "GET":
        return render_template("index.html",
                                today = today,
                                location = location,
                                weather = weather, 
                                temperature = temperature,
                                icon = icon,
                                filepath = filepath
                                )
    #テーブル表示
    if request.method == "POST":

        place_name = request.form.get('place_name')
        df = pd.read_csv("./csv/activekids3.csv")
        data = df[df['place'] == place_name]
        indoor = list(data["indoor"])[0]
        category = list(data["category"])[0]
        age = list(data["age"])[0]
        address = list(data["address"])[0]
        photo = list(data["photo"])[0]
        web = list(data["web"])[0]
        latitude = list(data["latitude"])[0]
        longitude = list(data["longitude"])[0]
        locations = list(data["locations"])[0]

        lst = ["place","indoor","category","age","address","photo","web","latitude","longitude","locations"]
        table = data[lst].T.to_html(header=False)

        # SQLデータベース
        con = get_db()
        pk = db.insert(con, place_name, indoor, category, age, address, photo, web, latitude, longitude, locations)
        results = db.select_all(con)
        ###

        #地図
        if place_name in list(df["place"]):
            df = df[df['place'] == place_name].reset_index(drop=True)

            lat = df['latitude'][0]
            lon = df['longitude'][0]

            map = folium.Map(location=[lat, lon], zoom_start=14)

            folium.Marker(location=[lat, lon], popup=place_name, icon=folium.Icon(color="purple", icon="flag")).add_to(map)          
            
            map_path = "./cache_file/" + datetime.now().strftime("%Y%m%d%H%M%S_") + "map.html"
            map.save(map_path)

        place_img = str(list(data["photo"])[0])
        if place_img =="nan":
            return render_template("index.html", 
                                    today = today,
                                    place_name=place_name, 
                                    indoor = indoor, 
                                    table=table,
                                    results = results,
                                    map_path=map_path,
                                    err_message_2="No image",
                                    location = location,
                                    weather = weather, 
                                    temperature = temperature,
                                    icon = icon,
                                    filepath = filepath
                                    )
        else:
            place_img = list(data["photo"])[0]
            filepath_img = './img/' + place_img + '.jpeg'
            return render_template("index.html", 
                                    today = today,
                                    place_name=place_name,
                                    indoor = indoor,
                                    table=table,
                                    results = results,
                                    map_path=map_path,
                                    filepath_img=filepath_img,
                                    location = location,
                                    weather = weather, 
                                    temperature = temperature,
                                    icon = icon,
                                    filepath = filepath
                                    )

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=1056) # ポートの変更