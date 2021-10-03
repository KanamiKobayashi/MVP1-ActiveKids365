import os
from datetime import datetime
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

@app.route("/", methods=["GET","POST"])

def main():
    if request.method == "GET":
        return render_template("index3.html")

    if request.method == "POST":

        place = request.form.get('place')
        indoor = request.form.get('indoor')
        category = request.form.get('category')
        age = request.form.get('age')
        address = request.form.get('address')
        photo = request.form.get('photo')
        web = request.form.get('web')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        locations = request.form.get('locations')

        con = get_db()
        pk = db.insert(con, place, indoor, category, age, address, photo, web, latitude, longitude, locations)
        results = db.select_all(con)

        df = pd.read_sql('select place, indoor, category, age, address, photo, web, latitude, longitude, locations from results', con=con)
        filepath = "./csv/" + datetime.now().strftime("%Y%m%d%H%M%S_data") + ".csv"
        df.to_csv(filepath, index=False)
        return render_template("index3.html", 
                                results=results,
                                message="Saved in database.")

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=1058) # ポートの変更