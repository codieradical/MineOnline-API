from flask import Response, request, make_response, abort, redirect, render_template
import json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
from uuid import uuid4
import bcrypt
from utils.modified_utf8 import utf8m_to_utf8s, utf8s_to_utf8m
from datetime import datetime
from io import BytesIO, StringIO
from utils.email import send_email
import re
from routes import serve
from utils.servers import *
from PIL import Image
from utils.database import getclassicservers

ALLOWED_EXTENSIONS = ['png', 'mine', 'dat']
MAX_WORLD_SIZE = 10000000 # 10 MB

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.')[-1].lower() in ALLOWED_EXTENSIONS

def filterClassicServers(x):
    return x['versionName'].lower()[0] == 'c'
def filterIndevServers(x):
    return x['versionName'].lower()[0] == 'i'
def filterAlphaServers(x):
    return x['versionName'].lower()[0] == 'a'
def filterBetaServers(x):
    return x['versionName'].lower()[0] == 'b'
def filterOtherServers(x):
    return x['versionName'].lower()[0] != 'c' and x['versionName'].lower()[0] != 'i' and x['versionName'].lower()[0] != 'a' and x['versionName'].lower()[0] != 'b'

def register_routes(app, mongo):
    @app.route('/')
    def index():
        return serve("index")

    @app.route('/servers')
    def classicservers():
        if not request.is_secure:
            return redirect(request.url.replace('http://', 'https://'))

        mineOnlineServers = getclassicservers(mongo)
        featuredServers = list(mongo.db.featuredservers.find())
        featuredServers = [dict(server, **{'isMineOnline': False}) for server in featuredServers]
        servers = mineOnlineServers + featuredServers

        usersCount = 0
        privateCount = 0
        for server in servers:
            if 'users' in server:
                usersCount = usersCount + int(server['users'])
            if 'public' in server and  server['public'] == "false":
                privateCount = privateCount + 1
            
        timeString = datetime.utcnow().strftime("%H:%M") + " (UTC) " + datetime.utcnow().strftime("%B %d")

        def mapServer(x): 
            if(not"md5" in x):
                return
            if(not "whitelisted" in x):
                return

            if ("public" in x and x["public"] == False):
                return

            status = NONE

            if (x["onlinemode"] == True or x["onlinemode"] == "true"):
                status = ONLINEMODE
            
            if (x["whitelisted"] == True and "whitelistUsers" in x and "whitelistIPs" in x):
                status = WHITELISTED

            return { 
                "createdAt": str(x["createdAt"]) if "createdAt" in x else None,
                "ip": x["ip"] if status != BANNED and status != NOT_ON_THE_WHITELIST else None,
                "port": x["port"] if status != BANNED and status != NOT_ON_THE_WHITELIST else None,
                "users": x["users"] if "users" in x else "0",
                "maxUsers": x["maxUsers"] if "maxUsers" in x else "24",
                "name": x["name"],
                "onlinemode": x["onlinemode"],
                "md5": x["md5"],
                "isMineOnline": x["isMineOnline"] if "isMineOnline" in x else True,
                "status": status,
                "versionName": x["versionName"] if "versionName" in x else None,
                "players": x["players"] if "players" in x else []
            }

        servers = list(map(mapServer, servers))
        servers = list(filter(filterServer, servers))
        serverCount = len(servers)

        classicServers = list(filter(filterClassicServers, servers))
        indevServers = list(filter(filterIndevServers, servers))
        alphaServers = list(filter(filterAlphaServers, servers))
        betaServers = list(filter(filterBetaServers, servers))
        # releaseServers = list(filter(filterReleaseServers, servers))
        otherServers = list(filter(filterOtherServers, servers))



        return render_template("public/servers.html", 
            classicServers=classicServers,
            indevServers=indevServers,
            alphaServers=alphaServers,
            betaServers=betaServers,
            otherServers=otherServers,
            serverCount=serverCount,
            usersCount=usersCount,
            privateCount=privateCount,
            timeString=timeString,
        )