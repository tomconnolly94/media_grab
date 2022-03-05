#!/venv/bin/python

# external dependencies
from flask import Flask, request, Response, send_from_directory
from dotenv import load_dotenv
from os.path import join, dirname
import os
import json

# internal dependencies
from server.controllers.PageServer import serveIndex
from server.controllers.DataServer import serveMediaInfo, submitMediaInfoRecord, deleteMediaInfoRecord, updateMediaInfoRecord, runMediaGrab, getSimilarShows

#create app
app = Flask(__name__, template_folder="client")

# load env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def getResponse(errorCode, errorMessage):
    return Response(errorMessage, status=errorCode, mimetype="text/html") 


@app.route("/", methods=["GET"])
def index():
    return serveIndex()


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'client/images'),
                          'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/MediaInfoRecords", methods=["GET"])
def MediaInfoRecords():
        return serveMediaInfo()


@app.route("/SimilarShows/<showTitle>", methods=["GET"])
def SimilarShows(showTitle):
        return getSimilarShows(showTitle)


@app.route("/MediaInfoRecord/<recordIndex>", methods=["POST", "PUT", "DELETE"])
def MediaIndexRecord(recordIndex):
    if request.method == "POST":
        submitMediaInfoRecord(json.loads(request.data))
        return getResponse(200, "got post request, all good") 
    elif request.method == "DELETE":
        if deleteMediaInfoRecord(int(recordIndex)):
            return getResponse(200, "got delete request, all good")
        else:
            return getResponse(500, "delete request failed") 
    elif request.method == "PUT":
        if updateMediaInfoRecord(request.data, int(recordIndex)):
            return getResponse(200, "got put request, all good") 
        else:
            return getResponse(500, "put request failed") 
    else:
        getResponse(500, "request method unrecognised for this route") 


@app.route('/runMediaGrab', methods=["GET"])
def mediaGrab():
    if runMediaGrab():
        return getResponse(200, "run media grab accepted") 
    else:
        return getResponse(500, "run media grab failed") 


# @app.route("/node_modules/<module>", methods=["GET"])
# def nodeModule(module):
#     if ".map" in module:
#         return serveNodeModuleMapModule(module)
#     else:
#         return serveNodeModule(module)


# @app.route("/js/<module>", methods=["GET"])
# def customJsModule(module):
#     return serveCustomJsModule(module)


# @app.route("/css/<module>", methods=["GET"])
# def customCssModule(module):
#     return serveCustomCssModule(module)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
