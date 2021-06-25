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
    with open("cookies/labels.txt", "r") as labels_f:
        labels_string_builder = ""
        for line in labels_f:
            labels_string_builder += '"' + line.strip("\n") +'"' + ","
        print(labels_string_builder[:-1])
        labels = eval(labels_string_builder[:-1])

    return render_template("index.html", labels=labels)
