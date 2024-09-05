#!/venv/bin/python

# external dependencies
from flask import Flask, request, Response, send_from_directory
from dotenv import load_dotenv
from os.path import join, dirname
import os, sys
import json
import logging
rootDir = dirname(dirname(os.path.realpath(__file__)))
sys.path.append(rootDir) # make root directory accessible

# internal dependencies
from server.controllers.PageServer import serveIndex
from server.controllers.DataServer import serveMediaInfo, submitMediaInfoRecord, \
    deleteMediaInfoRecord, updateMediaInfoRecord, runMediaGrab, getSimilarShows, \
    getTorrentTitleList
from common.LoggingController import initLogging 

#create app
app = Flask(__name__, template_folder="client")

# load env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

initLogging() # init logging module

def getResponse(errorCode, errorMessage):
    return Response(errorMessage, status=errorCode, mimetype="text/html") 


@app.route("/", methods=["GET"])
def index():
    return serveIndex()


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'client/images'),
                          'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/media-info-records", methods=["GET"])
def MediaInfoRecords():
        return serveMediaInfo()


@app.route("/similar-shows/<showTitle>", methods=["GET"])
def SimilarShows(showTitle):
        return getSimilarShows(showTitle)


@app.route("/media-info-record/<recordIndex>", methods=["POST", "PUT", "DELETE"])
def MediaIndexRecord(recordIndex):
    if request.method == "POST":
        if submitMediaInfoRecord(json.loads(request.data)):
            return getResponse(200, "got post request, all good")
        else:
            return getResponse(400, "post request failed, bad request") 
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


@app.route('/run-media-grab', methods=["GET"])
def mediaGrab():
    if runMediaGrab():
        return getResponse(200, "run media grab accepted") 
    else:
        return getResponse(500, "run media grab failed")

@app.route('/torrent-titles/<searchTerm>', methods=["GET"])
def TorrentTitles(searchTerm: str):
    torrentTitles = getTorrentTitleList(searchTerm)[:30]
    if torrentTitles:
        return getResponse(200, json.dumps({"torrentTitles": torrentTitles })) 
    else:
        return getResponse(500, "run media grab failed")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
