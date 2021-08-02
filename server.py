from flask import Flask, request, render_template, flash, make_response, redirect, url_for
import datetime
import time
import atexit
import os 

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = "dev"
searchKey = ''
filters = ['','']
showComplete = False

@app.route('/')
def index():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def form():
    labels = getList("cookies/labels.txt")
    if request.method =="POST":
        if request.form.get("quotes"):
            return quotes()
        elif request.form.get("lego"):
            return lego()
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
        elif request.form.get("lego"):
            return lego()
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

@app.route('/lego', methods=['GET', 'POST'])
def lego():
    sets = getSetList()
    partsd = getPartDict(getSetList()[0])[1:]
    #print(partsd)
    #partsd = sorted(partsd, key = lambda i: (i['Have'], i['Missing'],i['Quantity']))
    parts = getPartList(partsd)
    print(sets)
    if request.method =="POST":
        # for i in range(len(parts)):
        #     print("")
        changeCount = False
        for i in range(len(partsd)):
                if request.form.get(str(partsd[i]['PartID'])+"+") or request.form.get(str(partsd[i]['PartID'])+"-"):
                    changeCount = True
        if request.form.get("counters"):
            return form()
        elif request.form.get("quotes"):
            return quotes()
        elif request.form.get("getparts") or request.form.get("go") or changeCount:
        
            
            try:
                catFilter = request.form.getlist("category")
            except: catFilter = ''
            try:
                colFilter = request.form.getlist("colour")
            except: colFilter = ''
            try:
                request.form['showcomplete']
                showComplete = True
            except:
                showComplete = False
            #print(catFilter,colFilter)
            #if request.form.get("getparts") or request.form.get("go"):
            searchKey = request.form['search']
            if request.form.get("getparts"):
                showComplete = False
                colFilter = ''
                catFilter = ''
                searchKey = ''
            #if request.form.get("getparts") or request.form.get("go"):
            setnum = request.form["set"]
            setnum = setnum[:setnum.find("set")]
            setName = getSetList()[int(setnum)-1]
            partsd = getPartDict(setName)
            for i in range(len(partsd)):
                if request.form.get(str(partsd[i]['PartID'])+"+"):
                    partsd = increment(setName,partsd[i]['PartID'],1)
                    break
                elif request.form.get(str(partsd[i]['PartID'])+"-"):
                    partsd = increment(setName,partsd[i]['PartID'],-1)
                    break
            if showComplete == False:
                partsd = removeCompleted(partsd)
            partsd = filter(partsd,catFilter,colFilter)
            partsd = search(partsd,searchKey)
            #print(partsd[293])
            
            partsd = sorted(partsd, key = lambda i: (i['Have'],i['Missing'],i['Quantity']),reverse=True)
             
            parts = getPartList(partsd)
            return render_template("lego.html", parts=parts,sets=sets,
            categories=getColLists(partsd,"Category"),
            colours=getColLists(partsd,"Colour"),
            search=searchKey,
            filteredby=str(filters[0])+str(filters[1]),
            showComplete = showComplete)

       
        
    #parts = getList("cookies/quotes.txt")           
    return render_template("lego.html",sets=sets)

def sortd(d,col):
    sortList(d)
    return d

def removeCompleted(d):
    temp = []
    for r in d:
        if r['Missing'] != 0:
            temp.append(r)
    return temp
def increment(set,partID,amount):
    partsd = getPartDict(set)
    d = {"SetNumber":"","PartID":0,"Quantity":0,"Colour":"","Category":"","DesignID":0,"PartName":"","ImageURL":"","SetCount":0,"Have":0,"Missing":0}

    f = open("data/"+set,'w',encoding='utf-8')
    f.write(str(list(d.keys()))[1:-1].replace("'",'"'))
    f.write('\n')
    for di in partsd:
        if di['PartID'] == partID:
            if di['Have']+amount<=di['Quantity'] and di['Have']+amount>=0:
                di['Have']+=amount
            di['Missing'] = di['Quantity'] - di['Have']
    
    #print(str(list(d[1].values()))[1:-1].replace("'",'"').replace(", ",',')) 
        f.write('"'+str(list(di.values()))[2:-1].replace(", ",',').replace("','",'","').replace("',",'",').replace(",'",',"'))
        f.write('\n')
    f.close()
    return getPartDict(set)
    



def filter(d,categories=filters[0],colours=filters[1]):
    #filter
    if categories!=filters[0]:
        filters[0] = categories
    if colours!=filters[0]:
        filters[1] = colours
    if len(categories) == 0 and len(colours) == 0:
        return d
    temp = []
    for r in d:
        if len(categories) == 0 or len(colours) == 0:
            if r['Category'] in categories or r['Colour'] in colours:
                temp.append(r)
        else:
            if r['Category'] in categories and r['Colour'] in colours:
                temp.append(r)
    return temp

def search(d, key = searchKey):
    temp = []
    if key =="":
        return d
    for r in d:
        if key.lower() in str(r.values()).lower():
            temp.append(r)
    return temp
def getColLists(d,col):
    l = []
    for r in d:
        if not r[col] in l:
            l.append(r[col])
    return l


def getSetList():
    return os.listdir("data")
def getPartDict(set):
    d = {"SetNumber":"","PartID":0,"Quantity":0,"Colour":"","Category":"","DesignID":0,"PartName":"","ImageURL":"","SetCount":0,"Have":0,"Missing":0}
    #"10188-1",9339,6,"Black","Figure Parts",73200,"MINI BODY LOWER PART BLACK","https://www.lego.com/cdn/product-assets/element.img.lod5photo.192x192/9339.jpg",899
    #"10188-1",249626,2,"Black","Tyres And Rims, Special",2496,"WHEEL AXLE Ø8.2/Ø1.9","https://www.lego.com/cdn/product-assets/element.img.lod5photo.192x192/249626.jpg",280
    f = open("data/"+set,'r',encoding='utf-8')
    l = f.readlines()
    parts = []
    keys = list(d.keys())
    l = l[1:]
    #print(len(l))
    #return keys
    for li in l:
        temp = processRecord(li)
        tempD = d.copy()
        #print(temp)
        for i in range(len(temp)):
            try:
                tempD[keys[i]] = temp[i]
            except:
                print(i)
       
        if tempD['Quantity'] != 0:
            tempD['Missing'] = int(tempD['Quantity']) - int(tempD['Have'])
            parts.append(tempD)
            
    #print(parts[0])
    #print(parts[1])
    return parts

def processRecord(r):
    l = []
    #print(r)
    r = r.strip()
    while(len(r)>0):
        if r[0] == '"':
            r = r[1:]
            l.append(str(r[:r.index('"')]))
            r = r[r.index('"')+2:]
        else:
            if r.find(",") != -1:
                l.append(int(r[:r.index(',')]))
                r = r[r.index(',')+1:]
            else:
                l.append(int(r))
                r = ''

    return l

        

def getPartList(d):
    parts = []
    for di in d:
        parts.append(list(di.values()))
    return parts


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
