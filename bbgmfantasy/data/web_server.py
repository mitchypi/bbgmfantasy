from re import L
from flask import Flask, request, render_template, jsonify, redirect, url_for
import settings
import sqlite3
import os
from collections import defaultdict
from inference_example import generate
import torch
import time
import werkzeug

# Flask constructor
app = Flask(__name__)  
 

# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def home():
    upload_location = ""
    strsql = 'select distinct labelSet from labels'
    with createcdbcursor() as conn:
                cursor = conn.cursor()
                cursor.execute(strsql)
                allLabel = cursor.fetchall()
    if request.method == 'POST':
        label = request.form.get("labelSelect1")
        if 'query_image' in request.files:
            filetoprocess = request.files['query_image']
            if filetoprocess.filename:
                upload_location = os.path.join(settings.storage_location, "upload", f"{time.time()}_{werkzeug.utils.secure_filename(filetoprocess.filename)}")
                filetoprocess.save(upload_location)
                hashmap = load(label)
                x = generate(hashmap, upload_location)
                return render_template('view_set_results.html', labels=x, name = label)
        
    return render_template('home.html', labels=allLabel)       



@app.route('/add_labels', methods =["GET", "POST"])
def add_labels():
    if request.method == "POST":
       # getting input with name = fname in HTML form
        label = request.form.get("label1")
        set1 = request.form.get("set1")
        set1 = set1.strip()
        l = label.split('\n')
        print(l)
        for i in l:
            i = i.strip()
            if i:
                print(i)
                with createcdbcursor() as conn:
                    try:
                        sqlstr = f"INSERT INTO labels (labelSet,label) VALUES('{set1}','{i}')"
                        cursor = conn.cursor()
                        cursor.execute(sqlstr)
                    except sqlite3.IntegrityError:
                        print("removing duplicate")
    return render_template("form.html")    


@app.route('/view_sets', methods =["GET"])
def view_sets():
    strsql = 'select distinct labelSet from labels'
    with createcdbcursor() as conn:
            cursor = conn.cursor()
            cursor.execute(strsql)
            allLabel = cursor.fetchall()
            if allLabel:
                return render_template('view_sets.html', list=allLabel)

            else:
                return jsonify({'No handwriting samples!'})  


@app.route('/view_set/',defaults={'labelset': -1},methods =["GET", "POST"]) #grab text_id for better consistency
@app.route('/view_set/<labelset>', methods =["GET", "POST"])
def view_set(labelset):
    input = labelset
    if labelset != -1:
        strsql = f"select labelSet,label from labels where labelSet = '{labelset}'"

    else:
        return jsonify({'Please use a valid sample !'})

    with createcdbcursor() as conn:
        cursor = conn.cursor()
        cursor.execute(strsql)
        allLabels = cursor.fetchall()
    if request.method == "POST":
       # getting input with name = fname in HTML form
        label = request.form.get("label1")
        l = label.split('\n')
        print(l)
        for i in l:
            i = i.strip()
            if i:
                print(i)
                with createcdbcursor() as conn:
                    try:
                        sqlstr = f"INSERT INTO labels (labelSet,label) VALUES('{labelset}','{i}')"
                        cursor = conn.cursor()
                        cursor.execute(sqlstr)
                    except sqlite3.IntegrityError:
                        print("removing duplicate")
        with createcdbcursor() as conn:
            cursor = conn.cursor()
            cursor.execute(strsql)
            allLabelsUpdated = cursor.fetchall()
        return render_template('view_set.html', labels=allLabelsUpdated, name = labelset)
    return render_template('view_set.html', labels=allLabels, name = labelset)


@app.route('/delete/<labelset>/<label>', methods =["GET", "POST"])
def delete(labelset, label):
    strsql = f"delete from labels where labelSet = '{labelset}' and label = '{label}'"
    with createcdbcursor() as conn:
        cursor = conn.cursor()
        cursor.execute(strsql)
    return redirect(url_for('view_set',labelset = labelset))


@app.route('/delete_set/<labelset>/', methods =["GET", "POST"])
def delete_set(labelset):
    strsql = f"delete from labels where labelSet = '{labelset}'"
    with createcdbcursor() as conn:
        cursor = conn.cursor()
        cursor.execute(strsql)
    return redirect(url_for('view_sets'))


def load(labelset):
    strsql = f"select label from labels where labelSet = '{labelset}'"
    with createcdbcursor() as conn:
        cursor = conn.cursor()
        cursor.execute(strsql)
        allLabels = cursor.fetchall()

        if allLabels:
            hashmap = []
            for row in allLabels:
                hashmap.append(row[0])
            return hashmap
        else:
            return ('nothing...')


def createcdbcursor():
    _UserDB = sqlite3.connect(settings.dblocation, timeout=10)      #settings. set long timeout to avoid conflict.
    _UserDB.row_factory = sqlite3.Row
    return _UserDB

def CreateDB():
    with createcdbcursor() as conn:
        cursor = conn.cursor()
        with  open("data/create.sql") as sql_file:
            sql_as_string = sql_file.read()
            cursor.executescript(sql_as_string)
            cursor.execute("PRAGMA busy_timeout=1000;")      #settings. set long timeout to avoid conflict.
            conn.commit()
    print(f" Database is created in {settings.dblocation}")


def init():
    print(torch.cuda.is_available())
    print("HI init")
    if not os.path.exists(settings.dblocation):
        CreateDB()
    


init()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=True)
