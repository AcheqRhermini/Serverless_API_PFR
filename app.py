import json
#import numpy as np
from flask import Flask, request, jsonify
from flasgger import Swagger
from flasgger.utils import swag_from
from flasgger import LazyString, LazyJSONEncoder
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for
import os
import csv
import base64
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'csv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

output={}
app = Flask(__name__)
app.config["SWAGGER"] = {"title": "Swagger-UI", "uiversion": 2}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/api_rest_swagger/",
}

template = dict(
    swaggerUiPrefix=LazyString(lambda: request.environ.get("HTTP_X_SCRIPT_NAME", ""))
)

app.json_encoder = LazyJSONEncoder

swagger = Swagger(app, config=swagger_config, template=template)

@app.route("/")

def index():
    print(app.config)
    return "MetaData & Data API"


@app.route("/MetaData-file-API", methods=["POST"])
@swag_from("swagger_Rest_API_config.yml")
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp

    file = request.files['file']

    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_name= file.filename
        file_name = file_name.split(".")

        if file_name[1] == 'txt':
            metadata_txt = {}
            data_txt={}
            file_tmp = request.files['file'].read()
            file_tmp = file_tmp.decode("utf8")
            metadata_txt['file name']=file_name[0]
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            metadata_txt['file size']=file_length
            metadata_txt['file type']=file_name[1]
            
            output['File Data']= file_tmp
            output['File MetaData'] = metadata_txt
            return jsonify(output)

        elif file_name[1] == 'csv':
            metadata_csv={}
            fileString = file.read().decode('utf-8')
            datafile = [{k: v for k, v in row.items()} for row in csv.DictReader(fileString.splitlines(), skipinitialspace=True)]
            metadata_csv['file name']=file_name[0]
            metadata_csv['file type']=file_name[1]
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            metadata_csv['file size']= file_length
            output['File Data']= datafile
            output['File MetaData'] = metadata_csv
            return jsonify(output)

        elif file_name[1]=='png':
            metadata_png={}
            encoded_string = base64.b64encode(file.read())
            encoded_string = encoded_string.decode('utf-8')
            metadata_png['file name']=file_name[0]
            file.seek(0,os.SEEK_END)
            file_length = file.tell()
            metadata_png['file type']=file_name[1]
            metadata_png['file size']= file_length          
            #encoded_string = base64.b64encode(file.read().decode('utf-8'))
            output['File data']=encoded_string
            output['File Metadata']=metadata_png
            return jsonify(output)


    else:
        resp = jsonify({'message' : 'Allowed file types are txt, csv, png'})
        resp.status_code = 400
        return resp


if __name__ == "__main__":
    app.run(debug=True, port=443, host="0.0.0.0")

