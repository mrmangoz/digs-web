from flask import Flask, request, render_template, flash, make_response, redirect, url_for
import datetime
import dateutil.parser
import time
import atexit

from werkzeug.utils import secure_filename

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = "dev"



@app.route('/')
def index():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def form():
    labels = getList("cookies/labels.txt")
    if request.method =="POST":
        if request.form.get("quotes"):
            return quotes()
        elif request.form.get("addtally"):
            try: 
                request.form["autoincrement"]
                increment = True
            except:
                increment = False
            name = request.form["new_tally_name"]
            name = name.replace("\n","")
            dupe = False
            for l in labels:
                if name in l[0]:
                    dupe = True
            if not dupe and name.strip()!="":
                new_counter = [name,increment,0]
                labels.append(new_counter)
        else:
            for i in range(len(labels)):
                if request.form.get(str(i+1)+"d"):
                    labels.remove(labels[i])
                    break
                elif request.form.get(str(i+1)+"+"):
                    labels[i][2]+=1
                    break
                elif request.form.get(str(i+1)+"-"):
                    labels[i][2]-=1
                    break
                elif request.form.get(str(i+1)+"r"):
                    labels[i][2]=0
                    break
        with open("cookies/labels.txt","w") as labels_f:
            labels = sortList(labels)
            labels_f.write(str(labels))
    
    #print(labels)
    labels = getList("cookies/labels.txt")
    return render_template("index.html", labels=labels)

@app.route('/outofcontext', methods=['GET', 'POST'])
def quotes():
    if request.method =="POST":
        if request.form.get("postquote"):
            new_quote = request.form["newquote"]
            user = request.form["homies"]
            new_item = [new_quote.strip(),user,datetime.datetime.now().strftime("%d/%m/%Y")]
            quotes = getList("cookies/quotes.txt")
            if new_quote.strip() !="":
                quotes.append(new_item)
            with open("cookies/quotes.txt", "w") as quotes_f:
                    quotes_f.write(str(quotes))
        elif request.form.get("counters"):
            return form()
        else:
            quotes = getList("cookies/quotes.txt")
            for i in range(len(quotes)):
                if request.form.get(str(i+1)):
                    quotes.remove(quotes[i])
                    with open("cookies/quotes.txt", "w") as quotes_f:
                        quotes_f.write(str(quotes))
                    break



    
             
        #print(quotes)
    quotes = getList("cookies/quotes.txt")            
    return render_template("outofcontext.html", quotes=quotes)


def getList(file):
    with open(file, "r") as quotes_f:
        lines = quotes_f.readlines()
        line = ""
        for l in lines:
            line+=l
        if line.strip()=="":
            line="[]"
        return eval(line)
        
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
    counters = getList("cookies/labels.txt")
    for counter in counters:
        if counter[1] == True:
            counter[2]+=1
    with open("cookies/labels.txt", "w") as counters_f:
        counters_f.write(str(counters))
    print(datetime.datetime.now())

scheduler = BackgroundScheduler()
date = datetime.datetime.now()
scheduler.add_job(func=autoIncrement,trigger="cron",hour=0,minute=0,second=1)
scheduler.start()
atexit.register(lambda:scheduler.shutdown())
