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
    return render_template("index.html")
