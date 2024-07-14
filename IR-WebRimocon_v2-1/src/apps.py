### モジュールのインポート
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import pigpio

import THsesor_DHT20


### 以下でGPIOピン番号の登録と初期設定を行う
## もし赤外線受信モジュールをGPIO18以外に繋いだ場合は、gpio_irreadは18でなく繋いだピンの番号へ変更する
## もし赤外線LEDをGPIO17以外に繋いだ場合は、gpio_irroutは17でなく繋いだピンの番号へ変更する
gpio_irread = 17
gpio_irout = 18
pai = pigpio.pi()
pai.set_mode(gpio_irout, pigpio.OUTPUT)
pai.write(gpio_irout, 0)
pai.set_mode(gpio_irread, pigpio.INPUT)
pai.set_pull_up_down(gpio_irread, pigpio.PUD_UP)

app = Flask(__name__)
i2cad = 0x38


### コントローラ画面のエンドポイント
@app.route('/', methods=['GET', 'POST'])
def controller():
    ## "cmdlist"ファイル内に登録されているコマンド名を読み込む
    try:
        with open('cmdlist') as f:
            data = json.load(f)
    except:
        data = {}
    keys = list(data.keys())
    
    temp, humd = THsesor_DHT20.get_temp_humid(i2cad)
    thdata = [temp, humd]

    ## リクエストを受け取った際の操作
    if request.method == "POST":
        # コマンド登録完了画面で"back"ボタンが押された場合に、コントローラ画面を表示する
        if request.form["toggle"] == "back":
            return redirect(url_for("controller"))
        # トップ画面の赤外線コマンドボタンが押された場合に、os.systemを用いて該当する赤外線信号を発信する
        if request.form["toggle"] in keys:
            cmdname = request.form["toggle"]
            cmd = f'python3 irrp.py -p -g{gpio_irout} -f cmdlist {cmdname}'
            os.system(cmd)
            return redirect(url_for("controller"))
        # "AllOn"ボタンが押された場合、コマンド名に"on","ON","On"を含むコマンドを全て実行する
        if request.form["toggle"] == "AllOn":
            for key in keys:
                if type(key) != str:
                    continue
                elif ("on" in key) or ("ON" in key) or ("On" in key):
                    cmd = f'python3 irrp.py -p -g{gpio_irout} -f cmdlist {key}'
                    os.system(cmd)
        # "AllOff"ボタンが押された場合、コマンド名に"of","OFF","Off"を含むコマンドを全て実行する
        if request.form["toggle"] == "AllOff":
            for key in keys:
                if type(key) != str:
                    continue
                elif ("off" in key) or ("OFF" in key) or ("Off" in key):
                    cmd = f'python3 irrp.py -p -g{gpio_irout} -f cmdlist {key}'
                    os.system(cmd)
    return render_template("controller.html", data=data, thdata=thdata)


### コマンド登録画面のエンドポイント
@app.route('/add_cmd', methods=['GET', 'POST'])
def add_cmd():
    ## コントローラ画面で"+"ボタンが押された場合に、コマンド登録画面を表示する
    if request.method == "POST":
        return redirect(url_for("add_cmd"))
    return render_template("register.html")


### コマンド登録完了画面のエンドポイント
@app.route('/add_cmd/post', methods=['GET', 'POST'])
def add_post():
    ## コマンド登録画面で"Add"ボタンが押された場合に、コマンド登録完了画面を表示する
    if request.method == "POST":
        cmdname = request.form["command"]
        cmd = f"python3 irrp.py -r -g{gpio_irread} -f cmdlist {cmdname} --no-confirm --post 130"
        os.system(cmd)
        return redirect(url_for("add_post"))
    return render_template("handle.html")


@app.route('/THsensor')
def sensor_data():
    temp, humd = THsesor_DHT20.get_temp_humid(i2cad)
    dicst = {"T": temp, "H": humd}
    return jsonify(dicst)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
