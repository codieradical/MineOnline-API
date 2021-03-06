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
from utils.database import getservers

ALLOWED_EXTENSIONS = ['png', 'mine', 'dat']
MAX_WORLD_SIZE = 10000000 # 10 MB

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.')[-1].lower() in ALLOWED_EXTENSIONS

def filterFeaturedServers(x):
    return x['featured'] == True
def filterClassicServers(x):
    return x['versionName'].lower()[0] == 'c' and x['featured'] == False
def filterAlphaServers(x):
    return x['versionName'].lower()[0] == 'a' and x['featured'] == False
def filterBetaServers(x):
    return x['versionName'].lower()[0] == 'b' and x['featured'] == False
def filterOtherServers(x):
    return x['versionName'].lower()[0] != 'c' and x['versionName'].lower()[0] != 'a' and x['versionName'].lower()[0] != 'b' and x['featured'] == False

def register_routes(app, mongo):
    @app.route('/')
    def index():
        return serve("index")

    @app.route('/download')
    def download():
        return redirect("https://github.com/codieradical/MineOnline/releases/latest", 302)

    @app.route('/servers.jsp')
    def serversredirect():
        return redirect("/servers")

    @app.route('/servers')
    def servers():
        if not request.is_secure:
            return redirect(request.url.replace('http://', 'https://'))

        mineOnlineServers = getservers(mongo)
        staticservers = list(mongo.db.staticservers.find())
        staticservers = [dict(server, **{'isMineOnline': False}) for server in staticservers]
        servers = mineOnlineServers + staticservers

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

            onlinemode = x["onlinemode"]

            if x["name"] == "Oldcraft":
                onlinemode = False

            if "useBetaEvolutionsAuth" in x and x["useBetaEvolutionsAuth"] == True:
                onlinemode = True

            featured = False
            try:
                if mongo.db.featuredservers.find_one({"connectAddress": x["connectAddress"], "port": x["port"]}) != None:
                    featured = True
            except:
                pass

            return { 
                "createdAt": str(x["createdAt"]) if "createdAt" in x else None,
                "connectAddress": x["connectAddress"] if "connectAddress" in x else x["ip"],
                "connectAddress": x["connectAddress"] if "connectAddress" in x else x["ip"],
                "port": x["port"],
                "users": x["users"] if "users" in x else "0",
                "maxUsers": x["maxUsers"] if "maxUsers" in x else "24",
                "name": x["name"],
                "onlinemode": onlinemode,
                "md5": x["md5"],
                "isMineOnline": x["isMineOnline"] if "isMineOnline" in x else True,
                "versionName": x["versionName"] if "versionName" in x else None,
                "dontListPlayers": x["dontListPlayers"] if "dontListPlayers" in x else False,
                "motd": x["motd"] if "motd" in x else None,
                "players": x["players"] if "players" in x else [],
                "featured": featured,
                "useBetaEvolutionsAuth": x["useBetaEvolutionsAuth"] if "useBetaEvolutionsAuth" in x else False,
                "serverIcon": x["serverIcon"] if "serverIcon" in x else None,
                "whitelisted": x["whitelisted"] if "whitelisted" in x else False,
            }

        servers = list(map(mapServer, servers))
        servers = list(filter(filterServer, servers))
        serverCount = len(servers)

        featuredServers = list(filter(filterFeaturedServers, servers))
        classicServers = list(filter(filterClassicServers, servers))
        alphaServers = list(filter(filterAlphaServers, servers))
        betaServers = list(filter(filterBetaServers, servers))
        # releaseServers = list(filter(filterReleaseServers, servers))
        otherServers = list(filter(filterOtherServers, servers))



        return render_template("public/servers.html", 
            featuredServers=featuredServers,
            classicServers=classicServers,
            alphaServers=alphaServers,
            betaServers=betaServers,
            otherServers=otherServers,
            serverCount=serverCount,
            usersCount=usersCount,
            privateCount=privateCount,
            timeString=timeString,
        )