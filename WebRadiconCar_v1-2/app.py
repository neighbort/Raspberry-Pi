from flask import Flask, render_template, request, redirect, url_for, Response

api = Flask(__name__)

@api.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    api.run(host='0.0.0.0', port=334, ssl_context=('server.crt', 'server.key'), threaded=True, debug=True)