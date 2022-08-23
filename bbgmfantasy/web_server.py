from re import L
from flask import Flask, request, render_template, jsonify, redirect, url_for, Response
import settings
import sqlite3
import os
from collections import defaultdict
import csv
#import werkzeug
#import io
#import random
#import matplotlib
#import matplotlib.pyplot as plt
# Flask constructor
app = Flask(__name__)  

# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def home():
    upload_location = ""

    if request.method == 'POST':
        types = ["fga","fg", "fta", "ft", "3p", "pts", "trb", "ast", "stl", "blk", "tov", "dd", "td"]
        dontcheck = ["dd","td","\ufeff#"]
        values = defaultdict(lambda:0)
        x = request.form.get("defaults")
        if x:
            values = {"fga": -1, "fg": 2, "fta": -0.75, "ft": 1, "3p": 1, "pts": 1, "trb": 1.2, "ast": 1.5, "stl": 3, "blk": 3, "tov": -1, "dd": 2.5, "td": 5}
        else:
            for i in types:
                values[i] = request.form.get(i)
        
        if 'stats' in request.files:
            stat_file = request.files['stats']
            if stat_file.filename:
                upload_location =  os.path.join(settings.storage_location, stat_file.filename)
                stat_file.save(upload_location)
                with open(upload_location, newline='') as csvfile:
                    stats = csv.DictReader(csvfile)
                    results = {}
                    for row in stats:
                        points = get_points(row, values)
                        results[points[1]] = points[0]
                    avg = sum(results.values())/len(results) 
                    #url = create_plot(results)
                    return render_template('home.html', result = results, avg = avg)  
                    
        else:
            return render_template('home.html')   

    else:
        return render_template('home.html')
    

def check_dd(row, values):
    check = ["pts","ast","trb","stl","blk"]
    count = 0
    for key, value in row.items(): 
        if key.lower() in check:
            if int(value) >= 10:
                x = f"{key}: {value}"
                print(x)
                count+=1
    print(count)
    if count == 2:
        print("DOUBLE DOUBLE")
        return int(values["dd"])
    elif count >= 3:
        print("TRIPLE DOUBLE")
        return int(values["td"])
    else:
        return 0


def get_points(row, values):
    x = 0
    gameNum = row["\ufeff#"]
    for key, value in row.items():
        if key.lower() in values:
            pointVal = float(values[key.lower()])
            amount = int(value)
            x += pointVal*amount
    x += check_dd(row, values)
        
    return x,gameNum

"""
def create_plot(results):
    ordered = sorted(results.items())
    x, y = zip(*ordered)
    plt.stem(x,y)
    plt.ylabel('Fantasy Points')
    plt.xlabel('Game')
    plt.xticks(color = "None")
    plt.title('Fantasy Point trends')
    plt.savefig('static/storage/plot.png')
    url = 'static/storage/plot.png'
    return url
"""
#def read_stats(statFile):
    #return hi:

#def calculator(values, statline):
    



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
    if not os.path.exists(settings.dblocation):
        CreateDB()

#init()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=True)
