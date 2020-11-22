from flask import Response, request, make_response, abort
import json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
from uuid import uuid4, UUID
from utils.servers import *
from datetime import datetime, timedelta, timezone
from pymongo import IndexModel, ASCENDING, DESCENDING, errors
import sys
from utils.versions import get_versions
from utils.database import getclassicservers
from uuid import uuid4, UUID
import jwt
import socket
import requests
from utils.modified_utf8 import utf8s_to_utf8m
from io import BytesIO
import functools

def sort_servers(server2, server1):
    if server1["featured"]:
        return 1
    elif server2["featured"]:
        return -1
    else:
        return int(server1["users"]) - int(server2["users"])

def register_routes(app, mongo):
    @app.route("/api/servers/<uuid>", methods=["DELETE"])
    def deleteserver(uuid):
        mongo.db.classicservers.delete_one({"uuid": str(UUID(uuid))})
        return Response("ok", 200)

    @app.route("/api/servers/stats", methods=["GET"])
    def serverstats():
        servers = getclassicservers(mongo)
        servercount = len(servers)
        playercount = 0
        for server in servers:
            if "users" in server:
                playercount += int(server["users"])

        return Response(json.dumps({
            "serverCount": servercount,
            "playerCount": playercount
        }))

    @app.route("/api/servers", methods=["POST"])
    def addserver():
        #print(request.json["name"])
        
        port = request.json['port']
        maxUsers = request.json['max']
        name = str(request.json["name"])[:59]
        onlinemode = request.json['onlinemode']
        md5 = request.json['md5']
        whitelisted = request.json['whitelisted']
        uuid = str(uuid4())

        players = []
        if("players" in request.json):
            players = request.json["players"]

        motd = None
        if "motd" in request.json:
            motd = str(request.json["motd"])[:59]

        dontListPlayers = False
        if "dontListPlayers" in request.json:
            dontListPlayers = request.json["dontListPlayers"]

        versionName = "Unknown Version"

        if 'ip' in request.json and request.json['ip'] != '' and request.json['ip'] != '0.0.0.0':
            connectAddress = request.json['ip'] # new to mineonline to allow classic servers on different IPs
        else:
            connectAddress = request.remote_addr

        if connectAddress == "127.0.0.1":
            return Response("Can't list local servers.", 400)

        ip = socket.gethostbyname(connectAddress) 

        classicservers = mongo.db.classicservers

        if(port == None):
            port = "25565"

        versions = get_versions()

        for version in versions:
            if(version["md5"] == md5 and version["type"] == "server"):
                if('clientName' in version):
                    versionName = version["clientName"]
                elif('clientVersions' in version):
                    versionName = str(version["clientVersions"]).replace("'", "").replace("[", "").replace("]", "")
                else:
                    versionName = version["name"]
            pass

        try:
            # Find an existing salted server
            currentlisting = classicservers.find_one({"port": port, "ip": ip})
            expireDuration = timedelta(minutes = 2)

            # Delete existing server record
            classicservers.delete_many({"port": port, "ip": ip})

            users = request.json['users'] if 'users' in request.json else 0


            try:
                classicservers.insert_one({
                    "salt": currentlisting["salt"] if currentlisting != None and "salt" in currentlisting else None,
                    "createdAt": datetime.utcnow(),
                    "expiresAt": datetime.now(timezone.utc) + expireDuration,
                    "connectAddress": connectAddress,
                    "ip": ip,
                    "port": port,
                    "users": users,
                    "maxUsers": maxUsers,
                    "name": name,
                    "onlinemode": onlinemode,
                    "versionName": versionName,
                    "md5": md5,
                    "whitelisted": whitelisted,
                    "players": players,
                    "uuid": uuid,
                    "dontListPlayers": dontListPlayers,
                    "motd": motd
                })

            except Exception as err:
                #print(err)
                return Response("Something went wrong.", 500)


                        
            return make_response(json.dumps({
                "uuid": uuid
            }), 200)

        except Exception as e:
            return Response("Something went wrong.", 500)

        return Response("Something went wrong.", 500)

    @app.route("/api/servers", methods=["GET"])
    def listservers():
        mineOnlineServers = getclassicservers(mongo)
        featuredServers = list(mongo.db.featuredservers.find())
        featuredServers = [dict(server, **{'isMineOnline': False}) for server in featuredServers]
        servers = mineOnlineServers + featuredServers

        def mapServer(x): 
            if(not"md5" in x):
                return

            if ("public" in x and x["public"] == False):
                return

            onlinemode = x["onlinemode"]

            if x["name"] == "Oldcraft" or x["name"] == "RetroMC" or x["name"] == "BetaLands":
                onlinemode = False

            featured = False
            try:
                if mongo.db.serversfeatured.find_one({"connectAddress": x["connectAddress"], "port": x["port"]}) != None:
                    featured = True
            except:
                pass

            return { 
                "createdAt": str(x["createdAt"]) if "createdAt" in x else None,
                "ip": x["connectAddress"] if "connectAddress" in x else x["ip"],
                "connectAddress": x["connectAddress"] if "connectAddress" in x else x["ip"],
                "port": x["port"],
                "users": x["users"] if "users" in x else "0",
                "maxUsers": x["maxUsers"] if "maxUsers" in x else "24",
                "name": x["name"],
                "onlinemode": onlinemode,
                "md5": x["md5"],
                "isMineOnline": x["isMineOnline"] if "isMineOnline" in x else True,
                "players": x["players"] if "players" in x and (not "dontListPlayers" in x or x["dontListPlayers"] == False) else [],
                "motd": x["motd"] if "motd" in x else None,
                "dontListPlayers": x["dontListPlayers"] if "dontListPlayers" in x else False,
                "featured": featured
            }

        servers = list(map(mapServer, servers))
        servers = list(filter(filterServer, servers))
        servers.sort(key=functools.cmp_to_key(sort_servers))

        return Response(json.dumps(servers))

    @app.route("/api/getserver", methods=["GET"])
    def getserver():
        serverIP = request.args.get('serverIP')
        serverPort = request.args.get('serverPort')

        if serverIP.startswith("192.168") or serverIP == "127.0.0.1" or serverIP == "localhost" or serverIP == "0.0.0.0":
            serverIP = request.remote_addr

        if(serverPort == None):
            serverPort = "25565"

        try:
            server = mongo.db.classicservers.find_one({"port": serverPort, "ip": serverIP})
            if server == None:
                server = mongo.db.classicservers.find_one({"connectAddress": serverIP, "port": serverPort})
        except:
            pass

        if server == None:
            try:
                server = mongo.db.featuredservers.find_one({"port": serverPort, "ip": serverIP})

                if server == None:
                    server = mongo.db.featuredservers.find_one({"connectAddress": serverIP, "port": serverPort})
            except:
                pass

        if server == None:
            return Response("Server not found.", 404)

        if not "name" in server:
            return Response("Server not found.", 404)

        onlinemode = server["onlinemode"]

        if server["name"] == "Oldcraft" or server["name"] == "RetroMC" or server["name"] == "BetaLands":
            onlinemode = False
        
        def mapServer(x): 
            return { 
                "createdAt": str(x["createdAt"]) if "createdAt" in x else None,
                "connectAddress": x["connectAddress"] if "connectAddress" in x else x["ip"],
                "ip": x["ip"],
                "port": x["port"],
                "users": x["users"] if "users" in x else "0",
                "maxUsers": x["maxUsers"] if "maxUsers" in x else "24",
                "name": x["name"],
                "onlinemode": onlinemode,
                "md5": x["md5"],
                "isMineOnline": x["isMineOnline"] if "isMineOnline" in x else True,
                "players": x["players"] if "players" in x and (not "dontListPlayers" in x or x["dontListPlayers"] == False) else [],
                "motd": x["motd"] if "motd" in x else None,
                "dontListPlayers": x["dontListPlayers"] if "dontListPlayers" in x else False,
            }

        return Response(json.dumps(mapServer(server)))

    @app.route('/api/servertoken', methods=["POST"])
    def getmppass():
        accessToken = request.json['accessToken'] if "accessToken" in request.json else None 
        serverIP = request.json['serverIP']
        serverPort = request.json['serverPort']
        userID = request.json['userID'] if "userID" in request.json else None 
        username = request.json['username']

        if serverIP.startswith("192.168") or serverIP == "127.0.0.1" or serverIP == "localhost" or serverIP == "0.0.0.0":
            serverIP = request.remote_addr

        # decoded = jwt.decode(accessToken, verify=False)

        # if (decoded["spr"] != userID):
        #     return Response("Invalid Session", 401)

        sha_1 = hashlib.sha1()
        sha_1.update((serverIP + ":" + serverPort).encode("UTF-8"))
        serverId = sha_1.hexdigest()

        joinCheck = requests.get("https://sessionserver.mojang.com/session/minecraft/hasJoined?username=" + username + "&serverId=" + serverId + "&ip=" + serverIP)

        if joinCheck.status_code != 200 and joinCheck.status_code != 204:
            return Response("Invalid Session", 401)

        # usernameCheck = requests.get("https://api.mojang.com/users/profiles/minecraft/" + username)
        
        # if usernameCheck.status_code != 200:
        #     return Response("Bad username.", 400)

        # usernameCheck = json.loads(usernameCheck.content)

        # if not "id" in usernameCheck or usernameCheck["id"] != userID:
        #     return Response("Bad username.", 400)

        server = None

        try:
            server = mongo.db.classicservers.find_one({"ip": serverIP, "port": serverPort})
            if server == None:
                server = mongo.db.classicservers.find_one({"connectAddress": serverIP, "port": serverPort})

        except:
            pass

        if server != None:
            if "salt" in server and server['salt'] != None:
                mppass = str(hashlib.md5((server['salt'] + username).encode('utf-8')).hexdigest())
                return Response(mppass)

        try:
            if userID != None and accessToken != None:
                payload = len(username).to_bytes(2, byteorder='big') + utf8s_to_utf8m(username.encode("UTF-8")) + len("token:" + accessToken + ":" + userID).to_bytes(2, byteorder='big') + utf8s_to_utf8m(("token:" + accessToken + ":" + userID).encode("UTF-8"))

                betacraft_servers = requests.post("https://betacraft.pl/server.jsp", data=payload, headers={
                    "User-Agent": "Java/1.8.0_265",
                    "Content-type": "application/x-www-form-urlencoded"
                })
                mppass = betacraft_servers.content.decode("UTF-8")
                mppass = mppass[mppass.index("join://" + serverIP + ":" + serverPort + "/") + len("join://" + serverIP + ":" + serverPort + "/"):]
                mppass = mppass[:mppass.index("/")]
                if mppass == "-":
                    mppass = "0"
                return Response(mppass)
        except:
            pass

        return Response("Server not found.", 404)
