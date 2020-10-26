from flask import request, send_file, Response, render_template, redirect
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from os import path
from os import walk
from routes import serve
import socket
from glob import glob
import os

def register_routes(app, mongo):
    @app.route('/resources') # classic
    def resourcesIndex():
        if not request.is_secure:
            return redirect(request.url.replace('http://', 'https://'))
        resourcesRoot = "public/resources/"
        ls = [ f.path.replace(resourcesRoot, "") for f in os.scandir(resourcesRoot) if f.is_dir() ]
        return render_template("public/resources.html", resourceVersions=ls)