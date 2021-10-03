#app.py
import os
from flask import Flask, render_template, request, send_from_directory, g
import pandas as pd
import sqlite3
from datetime import datetime
import db

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, './db/db.sqlite3'),
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

SAVE_DIR = "img"
if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)

@app.route('/img/<path:filepath>')
def register_folder(filepath):
    return send_from_directory(SAVE_DIR, filepath)  

@app.route("/", methods=["GET","POST"])
def main():
    if request.method == "GET":
        return render_template("index2.html")
    if request.method == "POST":
        csv = request.files['csv']
        if csv:
            df = pd.read_csv(csv)
        else:
            return render_template("index2.html", err_message="ファイルを選択してください！")

        con = get_db()
        for i in range(len(df)):
            pk = db.insert(con, df.place[i], df.indoor[i], df.category[i], str(df.age[i]), df.address[i], df.photo[i], df.web[i], df.latitude[i], df.longitude[i], df.locations[i])
        results = db.select_all(con)

        return render_template("index2.html", 
                                results=results,
                                message="DBへのデータ登録が終了しました"
                                ) 

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=1057) # ポートの変更