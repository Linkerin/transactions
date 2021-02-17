from flask import Flask, render_template, redirect, request, jsonify
from analysis import Transactions
import os

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

    files = os.listdir('./temp')
    if len(files) == 2:
        transactions = Transactions()
        df = transactions.upload(f'./temp/{files[0]}', f'./temp/{files[1]}')

        if type(df) != str:
            result = transactions.full_analysis(df)
            result.to_excel('./temp/result.xlsx')
        else:
            return jsonify(status=df)

    for item in files:
        os.remove(f'./temp/{item}')

    return jsonify(status='OK')



if __name__ == '__main__':
    app.run(debug=True)