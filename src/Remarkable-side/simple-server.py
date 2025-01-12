#!/usr/bin/env python3

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return jsonify({
        "status": "success",
        "message": "reMarkable webserver is running!"
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "device": "reMarkable",
        "service": "webserver"
    })

if __name__ == '__main__':
    # 0.0.0.0 zorgt dat de server bereikbaar is vanaf andere apparaten
    # Debug mode uit voor productie
    app.run(host='0.0.0.0', port=5000, debug=False)