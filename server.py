from flask import Flask, request, render_template, flash, make_response, redirect, url_for
import datetime
import time
import atexit
import pymongo

from werkzeug.utils import secure_filename

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = "dev"
client = pymongo.MongoClient()
db = client.digs


@app.route('/')
def index():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def form():
    labels = getLabels()
    if request.method =="POST":
        if request.form.get("quotes"):
            return redirect('/outofcontext')
        elif request.form.get("addtally"):
            try:
                request.form["autoincrement"]
                increment = True
            except:
                increment = False
            name = request.form["new_tally_name"]
            name = name.strip("\n")
            dupe = False
            for l in labels:
                if name in l[0]:
                    dupe = True
            if not dupe and name != "":
                db.tallies.insert_one({"label":name, "status": increment, "count": 0})
        else:
            for i in range(len(labels)):
                if request.form.get(str(i+1)+"d"):
                    db.tallies.find_one_and_delete({"label": labels[i][0]})
                    break
                elif request.form.get(str(i+1)+"+"):
                    db.tallies.find_one_and_update({"label": labels[i][0]},
                                                   {"$inc" : {"count": 1}})
                    break
                elif request.form.get(str(i+1)+"-"):
                    db.tallies.find_one_and_update({"label": labels[i][0] },
                                                   {"$inc" : {"count": -1}})
                    break
                elif request.form.get(str(i+1)+"r"):
                    db.tallies.find_one_and_update({"label": labels[i][0]},
                                                   {"$set" : {"count": 0}})
                    break
        # with open("cookies/labels.txt","w") as labels_f:
        #     labels = sortList(labels)
        #     labels_f.write(str(labels))

    labels = getLabels()
    return render_template("index.html", labels=labels)

@app.route('/outofcontext', methods=['GET', 'POST'])
def quotes():
    if request.method =="POST":
        if request.form.get("postquote"):
            new_quote = str(request.form["newquote"].strip())
            user = str(request.form["homies"])
            date = str(datetime.datetime.now().strftime("%d/%m/%Y"))
            if new_quote != "":
                db.quotes.insert_one({"quote":new_quote,"author":user,"date":date})
        elif request.form.get("counters"):
            return redirect('/index')
        else:
            quotes = getQuotes()
            for i in range(len(quotes)):
                if request.form.get(str(i+1)):
                    db.quotes.find_one_and_delete({"quote": quotes[i][0]})
                    break
    quotes = getQuotes()

    return render_template("outofcontext.html", quotes=quotes)


def getQuotes():
    quotes = []
    for quote in db.quotes.find():
        quotes += [[quote["quote"], quote["author"], quote["date"]]]
    quotes.reverse()
    return quotes

def getLabels():
    labels = []
    for label in db.tallies.find():
        labels += [[label["label"], label["status"], label["count"]]]
    return sortList(labels)

def sortList(labels):
    for i in range(len(labels)):
        maxi = i
        for k in range(i,len(labels)):
            if labels[k][2]>labels[maxi][2]:
                maxi = k
        temp = labels[i]
        labels[i] = labels[maxi]
        labels[maxi] = temp
    return labels





def autoIncrement():
    for counter in db.tallies.find():
        if counter["status"]:
            db.tallies.find_one_and_update({"label": counter["label"]},
                                           {"$inc" : {"count": 1}})

scheduler = BackgroundScheduler()
date = datetime.datetime.now()
scheduler.add_job(func=autoIncrement,trigger="cron",hour=0,minute=0,second=1)
scheduler.start()
atexit.register(lambda:scheduler.shutdown())
