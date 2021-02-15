from flask import Flask, render_template, redirect, request, jsonify
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/upload", methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        for _, value in request.files.items():
            value.save(f'./temp/{value.filename}')
    return jsonify(status='OK')



if __name__ == '__main__':
    app.run(debug=True)