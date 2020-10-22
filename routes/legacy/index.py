from flask import request, send_file, Response
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from os import path
from os import walk
from routes import serve

from routes.legacy.levels import register_routes as register_levels_routes
from routes.legacy.website import register_routes as register_website_routes

def register_routes(app, mongo):
    register_levels_routes(app, mongo)
    register_website_routes(app, mongo)

    @app.route('/resources/') # classic
    def resourcesArray():
        return resourcesArrayVersioned("default")

    @app.route('/resources/<version>/') # classic
    def resourcesArrayVersioned(version):
        resourcesRoot = "public/resources/" + version
        if (not path.exists(resourcesRoot)):
            return Response("Resources not found.", 404)

        filenames = []
        for subdir, dirs, files in walk(resourcesRoot):
            for file in files:
                filenames.append(path.join(subdir, file).replace(resourcesRoot + "\\", "").replace("\\", "/"))

        res = ""
        for filename in filenames:
            filesize = path.getsize(resourcesRoot + "/" + filename)
            modified = path.getmtime(resourcesRoot + "/" + filename) * 1000
            res += ",".join([filename, str(filesize), str(int(modified))]) + "\r\n"

        return Response(res, mimetype="text/plain")

    @app.route('/MinecraftResources/')
    def resourcesTree():
        return resourcesTreeVersioned("default")

    @app.route('/MinecraftResources/<version>/')
    def resourcesTreeVersioned(version):
        resourcesRoot = "public/resources/" + version
        if (not path.exists(resourcesRoot)):
            return Response("Resources not found.", 404)

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
            filesize = path.getsize(resourcesRoot + "/" + filename)
            modified = path.getmtime(resourcesRoot + "/" + filename)
            res += "<Contents>\
                        <Key>" + filename + "</Key>\
                        <LastModified>" + datetime.utcfromtimestamp(modified).strftime('%Y-%m-%dT%H:%M:%S.000Z') + "</LastModified>\
                        <Size>" + str(filesize) + "</Size>\
                    </Contents>"

        res += "</ListBucketResult>"

        return Response(res, mimetype="text/xml")

    @app.route('/resources/<path:path>') # classic
    @app.route('/MinecraftResources/<path:path>') # classic
    def classicResourcesRedirect(path):
        return serve("/resources/default/" + path)

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
        if 'ip' in request.values and request.values['ip'] != "":
            ip = request.values['ip'] # new to mineonline to allow classic servers on different IPs
        else:
            ip = request.remote_addr

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