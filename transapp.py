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
                return jsonify(status='Pandas: invalid file type')

        transactions = Transactions()
        df = transactions.upload(f"./temp/{data['filenames'][0]}", f"./temp/{data['filenames'][1]}")
        if type(df) != str:
            result = transactions.full_analysis(df)
            result.to_excel('./temp/result.xlsx')
        else:
            return jsonify(status=df)
    print('Done')
    return send_from_directory('./temp', filename='result.xlsx', as_attachment=True,
                     cache_timeout=0,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # files = os.listdir('./temp')
    # for item in files:
    #     os.remove(f'./temp/{item}')


if __name__ == '__main__':
    app.run(debug=True)