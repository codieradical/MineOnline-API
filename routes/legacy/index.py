from flask import request, send_file, Response, render_template
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from os import path
from os import walk
from routes import serve
import socket
from glob import glob
import os

from routes.legacy.levels import register_routes as register_levels_routes
from routes.legacy.website import register_routes as register_website_routes
from routes.legacy.resources import register_routes as register_resources_routes

def register_routes(app, mongo):
    register_levels_routes(app, mongo)
    register_website_routes(app, mongo)
    register_resources_routes(app, mongo)

    #not sure when this was used, but it definately existed!
    @app.route('/haspaid.jsp')
    def haspaid():
        username = request.args.get('user')
        return Response("true")

    # unknown endpoint, found in infdev, may be in more.
    @app.route('/game/')
    def unknown1():
        username = request.args.get('n')
        sessionId = request.args.get('i')
        return Response("42069")

    """
    Classic server heartbeat route.
    This has been mostly replaced with mineonline's heartbeat.
    Currently it's only used to store the servers's salt.
    In future, this can be grabbed by mineonline and sent with the new heartbeat.
    """
    @app.route('/heartbeat.jsp', methods=["POST", "GET"])
    def addclassicserver(): 
        # If there's no salt, just use the standard list endpoint.
        if 'salt' not in request.values:
            return Response("https://mineonline.codie.gg/servers")

        port = request.values['port']
        users = request.values['users']
        maxUsers = request.values['max']
        name = request.values['name']
        public = request.values['public']
        salt = request.values['salt']
        if 'ip' in request.values and request.values['ip'] != "" and request.values['ip'] != "0.0.0.0":
            connectAddress = request.values['ip'] # new to mineonline to allow classic servers on different IPs
        else:
            connectAddress = request.remote_addr

        try:
            ip = socket.gethostbyname(connectAddress)
        except:
            ip = connectAddress

        if ip == "127.0.0.1":
            return Response("Can't list local servers.", 400)

        classicservers = mongo.db.classicservers

        user = None

        if(port == None):
            port = "25565"

        try:
            # Find an existing versioned server
            currentlisting = classicservers.find_one({"port": port, "ip": ip, "md5": {'$nin': [None, '']}})
            # Delete the rest
            expireDuration = timedelta(minutes = 2)
            if(currentlisting):
                _id = currentlisting['_id']
                classicservers.delete_many({"port": port, "ip": ip, "_id": {"$ne": _id}})
                classicservers.update_one({"_id": _id}, { "$set": {
                    "createdAt": datetime.utcnow(),
                    "expiresAt": datetime.now(timezone.utc) + expireDuration,
                    "connectAddress": connectAddress,
                    "ip": ip,
                    "port": port,
                    "users": users,
                    "maxUsers": maxUsers,
                    "name": name,
                    "public": public,
                    "salt": salt,
                }})

            else:
                # Delete existing server record
                classicservers.delete_many({"port": port, "ip": ip})
                _id = ObjectId()

                classicservers.insert_one({
                    "_id": _id,
                    "createdAt": datetime.utcnow(),
                    "expiresAt": datetime.now(timezone.utc) + expireDuration,
                    "ip": ip,
                    "connectAddress": connectAddress,
                    "port": port,
                    "users": users,
                    "maxUsers": maxUsers,
                    "name": name,
                    "public": public,
                    "salt": salt,
                })
            
            if (port != "25565"):
                return Response("https://mineonline.codie.gg/servers")
            else:
                return Response("https://mineonline.codie.gg/servers")

        except:
            return Response("Something went wrong.", 500)

        return Response("Something went wrong.", 500)

    @app.route('/login/session.jsp')
    def checksession():
        username = request.args.get('name')
        sessionId = request.args.get('session')

        # user = None
        
        # try:
        #     users = mongo.db.users
        #     user = users.find_one({"sessionId": ObjectId(sessionId), "user": username})

        #     if user and user['premium']:
        #         return Response("ok")
        #     else:
        #         return Response("Invalid Session", 400)
        # except:
        #     return Response("Invalid Session", 400)

        # return Response("Invalid Session", 400)

        return Response("ok")