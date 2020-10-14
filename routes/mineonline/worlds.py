from flask import Response, request, make_response, abort, redirect
import json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
from uuid import uuid4, UUID
from utils.modified_utf8 import utf8m_to_utf8s, utf8s_to_utf8m
from io import BytesIO, StringIO

def register_routes(app, mongo):
    # Download a classic world.
    @app.route('/level/download')
    def getWorld():
        username = request.args.get("username")
        worldId = request.args.get("worldId")
        userworlds = None
        mapId = str(int(worldId) - 1)

        try:
            userworlds = mongo.db.userworlds.find_one({"username" : username})
        except:
            return Response("User not found.", 404)

        if (userworlds == None):
            return Response("User not found.", 404)

        if mapId in userworlds:
            response = Response(userworlds[mapId]['data'], mimetype='application/x-mine')
            response.headers["content-disposition"] = "attachment; filename=" + userworlds[mapId]["name"] + ".mine"
            return response
        else:
            return Response("Map not found.", 404)