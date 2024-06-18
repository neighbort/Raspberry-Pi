from flask import Flask, render_template, request, redirect, url_for
import os
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def controller():
    try:
        with open('buttons.json') as f:
            data = json.load(f)
    except:
        data = {}
    keys = list(data.keys())

    if request.method == "POST":
        if request.form["toggle"] == "back":
            return redirect(url_for("controller"))
        if request.form["toggle"] in keys:
            cmdname = request.form["toggle"]
            cmd = f"mkdir {cmdname}"
            os.system(cmd)
            return redirect(url_for("controller"))
    return render_template("controller.html", data=data)

@app.route('/add_cmd', methods=['GET', 'POST'])
def add_cmd():
    if request.method == "POST":
        return redirect(url_for("add_cmd"))
    return render_template("register.html")

@app.route('/add_cmd/post', methods=['GET', 'POST'])
def add_post():
    if request.method == "POST":
        cmdname = request.form["command"]
        cmd = f"mkdir {cmdname}"
        #os.system(cmd)
        return redirect(url_for("add_post"))
    return render_template("handle.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)