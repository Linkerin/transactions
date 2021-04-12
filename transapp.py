"""
Accouting transactions fraud analysis application
Copyright (C) 2021  Alexey Gusev. All rights reserved
GNU Affero General Public License v3.0
Version: 0.1
License: https://github.com/Linkerin/transactions/blob/main/license.txt
"""

from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
from analysis import Transactions
import json
import os

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/upload", methods = ['POST'])
def upload():
    if request.method == 'POST':
        filenames = []
        for _, value in request.files.items():
            value.save(f'./temp/{value.filename}')
            filenames.append(value.filename)

    return jsonify(status='Upload completed', filenames=filenames)

@app.route("/pandas_upload", methods= ['GET', 'POST'])
def pandas_upload():
    if request.method == 'POST':
        data = json.loads(request.data)

        valid_types = ['xls', 'xlsx']
        for item in data['filenames']:
            if item.split('.')[-1] not in valid_types:
                return jsonify(status='Некорректный формат файла'), 415

        transactions = Transactions()
        if len(data['filenames']) == 2:
            df = transactions.upload(f"./temp/{data['filenames'][0]}",
                                     f"./temp/{data['filenames'][1]}")
        elif len(data['filenames']) == 3:
            df = transactions.upload(f"./temp/{data['filenames'][0]}",
                                     f"./temp/{data['filenames'][1]}",
                                     f"./temp/{data['filenames'][2]}")
        if type(df) != str:
            result = transactions.full_analysis(df)
            if type(result) != str:
                result.to_excel('./temp/result.xlsx')
            else:
                return jsonify(status=result), 415
        else:
            return jsonify(status=df), 415

    return send_from_directory('temp', 'result.xlsx', as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


if __name__ == '__main__':
    app.run(debug=True)

    items = os.listdir('./temp')
    for item in items:
        os.remove(f'./temp/{item}')
