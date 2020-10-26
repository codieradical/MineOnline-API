from flask import request, send_file, Response, render_template
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from os import path
from os import walk
from routes import serve
import socket
from glob import glob
import os

def register_routes(app, mongo):
    @app.route('/resources/') # classic
    def resourcesArray():
        return resourcesArrayVersioned("default")

    @app.route('/resources/<version>/') # classic
    def resourcesArrayVersioned(version):
        resourcesRoot = "public/resources/" + version
        if (not path.exists(resourcesRoot)):
            resourcesRoot = "public/resources/default" + version

        filenames = []
        for subdir, dirs, files in walk(resourcesRoot):
            for file in files:
                filenames.append(path.join(subdir, file).replace(resourcesRoot + "\\", "").replace("\\", "/"))

        res = ""
        for filename in filenames:
            filesize = path.getsize(path.join("./" + filename))
            modified = path.getmtime(path.join("./" + filename)) * 1000
            res += ",".join([filename.replace(resourcesRoot + "/", ""), str(filesize), str(int(modified))]) + "\r\n"

        return Response(res, mimetype="text/plain")

    @app.route('/MinecraftResources/')
    def resourcesTree():
        return resourcesTreeVersioned("default")

    @app.route('/MinecraftResources/<version>/')
    def resourcesTreeVersioned(version):
        resourcesRoot = "public/resources/" + version
        if (not path.exists(resourcesRoot)):
            resourcesRoot = "public/resources/default" + version

        filenames = []
        for subdir, dirs, files in walk(resourcesRoot):
            for file in files:
                filenames.append(path.join(subdir, file).replace(resourcesRoot + "\\", "").replace("\\", "/"))

        res = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\
                <ListBucketResult xmlns=\"http://s3.amazonaws.com/doc/2006-03-01/\">\
                <Name>MinecraftResources</Name>\
                <Prefix></Prefix>\
                <Marker></Marker>\
                <MaxKeys>1000</MaxKeys>\
                <IsTruncated>false</IsTruncated>"

        for filename in filenames:
            filesize = path.getsize(path.join("./" + filename))
            modified = path.getmtime(path.join("./" + filename))
            res += "<Contents>\
                        <Key>" + filename.replace(resourcesRoot + "/", "") + "</Key>\
                            <LastModified>" + datetime.utcfromtimestamp(modified).strftime('%Y-%m-%dT%H:%M:%S.000Z') + "</LastModified>\
                        <Size>" + str(filesize) + "</Size>\
                    </Contents>"

        res += "</ListBucketResult>"

        return Response(res, mimetype="text/xml")

    @app.route('/MinecraftResources/<path:path>') # classic
    def classicResourcesRedirect(path):
        return serve("resources/" + path)