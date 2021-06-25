from flask import Flask, request, render_template, flash, make_response, redirect, url_for
import datetime
import dateutil.parser


app = Flask(__name__)
app.secret_key = "dev"

@app.route('/')
def index():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def form():
    if request.method =="POST":
        if request.form.get("quotes"):
            return quotes()
    with open("cookies/labels.txt", "r") as labels_f:
        labels_string_builder = ""
        for line in labels_f:
            labels_string_builder += '"' + line.strip("\n") +'"' + ","
        print(labels_string_builder[:-1])
        labels = eval(labels_string_builder[:-1])

    return render_template("index.html", labels=labels)

@app.route('/outofcontext', methods=['GET', 'POST'])
def quotes():
    if request.method =="POST":
        if request.form.get("postquote"):
            new_quote = request.form["newquote"]
            user = request.form["homies"]
            with open("cookies/quotes.txt", "a") as quotes_f:
                if new_quote.strip() !="":
                    quotes_f.write("\n#" + new_quote + "-" + user +" "+ datetime.datetime.now().strftime("%d/%m/%Y"))
        elif request.form.get("counters"):
            return form()
        else:
            quotes = quoteList()
            for quote in quotes:
                query = (quote[0]+quote[1])
                #print(query)
                #print(request.form[query])
                if request.form.get(query):
                    #print("Found")
                    quotes.remove(quote)
                    with open("cookies/quotes.txt", "w") as quotes_f:
                        for line in quotes:
                            quotes_f.write("\n#" + line[0] +line[1].strip())
                    break



    
             
        #print(quotes)
    quotes = quoteList()            
    return render_template("outofcontext.html", quotes=quotes)


def quoteList():
    quotes = []
    with open("cookies/quotes.txt", "r") as quotes_f:
        lines = quotes_f.readlines()
        line = ""
        for l in lines:
            line+=l
        lines = line.split("#")
        #print(lines)
        for l in lines:
            temp = []
            temp.append(l[:l.find("-")])
            temp.append(l[l.find("-"):])
            if temp[0].strip() !="":
                quotes.append(temp)
    return quotes