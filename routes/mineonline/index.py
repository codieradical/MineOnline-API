from flask import Response, request, make_response, abort
import json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
from uuid import uuid4, UUID
from routes.mineonline.skins import register_routes as register_skins_routes
from routes.mineonline.servers import register_routes as register_servers_routes
from routes.mineonline.worlds import register_routes as register_worlds_routes
from routes.mineonline.mojang import register_routes as register_mojang_routes
import os
import bcrypt


def register_routes(app, mongo):
    register_skins_routes(app, mongo)
    register_servers_routes(app, mongo)
    register_worlds_routes(app, mongo)

    @app.route('/api/getmyip')
    def ipaddress():
        return make_response(json.dumps({
            "ip": request.remote_addr
        }), 200)

    @app.route('/api/versions')
    def versionsindex():
        indexJson = { "versions" : []}

        versionsPath = './public/versions/'

        for subdir, dirs, files in os.walk('./public/versions/'):
            for file in files:
                openFile = open(os.path.join(subdir, file))
                data = openFile.read().encode("utf-8")
                indexJson["versions"].append({
                    "name": file,
                    "url": os.path.join(subdir, file).replace(versionsPath, "/public/versions/").replace("\\", "/"),
                    "modified": os.path.getmtime(os.path.join(subdir, file)),
                })

        res = make_response(json.dumps(indexJson))
        res.mimetype = 'application/json'
        return res

    # Used when joining a server to get a response the game will recognize.
    @app.route('/api/ok')
    def stubok():
        return Response("ok")