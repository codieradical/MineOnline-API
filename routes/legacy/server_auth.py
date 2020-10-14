from flask import Response, request, make_response, abort
import json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
from uuid import uuid4
import bcrypt
from datetime import datetime

def register_routes(app, mongo):
    @app.route('/game/joinserver.jsp')
    def joinserver():
        username = request.args.get('user')
        sessionId = request.args.get('sessionId')
        serverId = request.args.get('serverId')

        if not 'sessionId' in request.args or sessionId == None:
            return Response("Invalid Session: you are not logged in.")

        serverjoins = mongo.db.serverjoins

        user = None

        try:
            users = mongo.db.users
            user = users.find_one({"sessionId": ObjectId(sessionId), "user": username})

            if not user:
                return Response("Invalid Session")
            if not user['premium']:
                return Response("User not premium.")

            serverjoins.delete_many({"user": username})

            serverjoins.insert_one({
                "createdAt": datetime.utcnow(),
                "playerName": user["user"],
                "serverId": serverId,
            })

            response = Response("ok")
            return response
        except:
            return Response("Invalid Session")

        return Response("Something went wrong.")

    @app.route('/game/checkserver.jsp')
    def checkserver():
        username = request.args.get('user')
        serverId = request.args.get('serverId')

        serverjoins = mongo.db.serverjoins

        try:
            found = serverjoins.find_one({"playerName": username, "serverId": serverId})
            if not found:
                return Response("Invalid Session", 401)

            serverjoins.delete_one({"_id": found['_id']})

            response = Response("YES")
            return response
        except:
            return Response("Invalid Session", 401)

        return Response("Invalid Session", 401)