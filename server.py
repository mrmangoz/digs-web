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
            if not dupe:
                new_counter = [name,increment,0]
                labels.append(new_counter)
                with open("cookies/labels.txt","w") as labels_f:
                    labels_f.write(str(labels))
                


    # with open("cookies/labels.txt", "r") as labels_f:
    #     labels_string_builder = ""
    #     for line in labels_f:
    #         labels_string_builder += '"' + line.strip("\n") +'"' + ","
    #     print(labels_string_builder[:-1])
    #     labels = eval(labels_string_builder[:-1])
    
    print(labels)
    #autoIncrement()
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
