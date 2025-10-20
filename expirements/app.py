# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 11:20:04 2022

@author: 51148
"""
from flask import request, Blueprint,Flask
from flask_cors import CORS, cross_origin
from pdf_comparison import *
from extract_compare_highlight import *
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.route('/comparePdf', methods=['GET','POST'])
def compare_pdf():
    if request.method == 'POST':
        source_highlighted, destination_highlighted = compare_and_highlight_pdf(request.form['soucePdfPath'],
            request.form['destinationPdfPath'])
        final_report = create_final_highlighted_report(source_highlighted, destination_highlighted,
        testcase_name=request.form['testcaseName'],
        testcase_description=request.form['testCaseDescription'],
        app_version=request.form['appVersion'],
        aut_version=request.form['autVersion'],
        generated_at=request.form['generatedAt'],
        generated_by=request.form['generatedBy'])
        return_data = {
            "message": "Comparison Successful!",
            "sourceHighlightedPdf": source_highlighted,
            "destinationHighlightedPdf": destination_highlighted,
            "finalReport": final_report
        }
        return json.dumps(return_data)
    else:
        return json.loads(''' {
            "message" : "API connection is successful",
            "requestFormat": "POST - FormData - soucePdfPath, destinationPdfPath"
        } ''')

@app.route('/upload-pdf', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        filename = file.filename
        # Here you should save the file
        path = "C:/tmp/" + filename
        file.save(path)
        return_data = {
            "message": "Upload Successful!",
            "path": path
        }
        return json.dumps(return_data)
    return_data = {
            "message": "Upload UnSuccessful!",
    }
    return json.dumps(return_data)

if __name__ == '__main__':
 
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()