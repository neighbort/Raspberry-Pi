from flask import Flask, render_template, request, redirect, url_for
import os
import json

gpio_irread = 'g18'
gpio_irout = 'g17'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def controller():
    try:
        with open('cmdlist') as f:
            data = json.load(f)
    except:
        data = {}
    keys = list(data.keys())

    if request.method == "POST":
        if request.form["toggle"] == "back":
            return redirect(url_for("controller"))
        if request.form["toggle"] in keys:
            cmdname = request.form["toggle"]
            cmd = f'python3 irrp.py -p -{gpio_irout} -f cmdlist {cmdname}'
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
        cmd = f"python3 irrp.py -r -{gpio_irread} -f cmdlist {cmdname} --no-confirm --post 130"
        os.system(cmd)
        return redirect(url_for("add_post"))
    return render_template("handle.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)