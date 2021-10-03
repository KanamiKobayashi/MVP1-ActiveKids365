import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash

def select_all(con):
    cur = con.execute('select id, place, indoor, category, age, address, photo, web, latitude, longitude, locations, created from results order by id desc')
    return cur.fetchall()
 
 
def select(con, pk):
    cur = con.execute('select id, place, indoor, category, age, address, photo, web, latitude, longitude, locations, created from results where id=?', (pk,))
    return cur.fetchone()
 
 
def insert(con, place, indoor, category, age, address, photo, web, latitude, longitude, locations):
    cur = con.cursor()
    cur.execute('insert into results (place, indoor, category, age, address, photo, web, latitude, longitude, locations) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [place, indoor, category, age, address, photo, web, latitude, longitude, locations])
    pk = cur.lastrowid
    con.commit()
    return pk
 
def delete(con, pk):
    cur = con.cursor()
    cur.execute('delete from results where id=?', (pk,))
    con.commit()
 