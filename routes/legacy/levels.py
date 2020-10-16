
from flask import Response, request, make_response, abort
import json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
from uuid import uuid4
import bcrypt
from utils.modified_utf8 import utf8m_to_utf8s, utf8s_to_utf8m
from datetime import datetime

''' Register classic level save / load / list routes '''
def register_routes(app, mongo):
    #classic
    @app.route('/listmaps.jsp')
    def listmaps():
        username = request.args['user']
        maps = None

        try:
            userworlds = mongo.db.userworlds.find_one({"username" : username})
        except:
            return Response("User not found.", 404)

        if (userworlds == None):
            return Response("-;-;-;-;-")

        return Response(';'.join([
            userworlds['0']['name'] if '0' in userworlds else '-',
            userworlds['1']['name'] if '1' in userworlds else '-',
            userworlds['2']['name'] if '2' in userworlds else '-',
            userworlds['3']['name'] if '3' in userworlds else '-',
            userworlds['4']['name'] if '4' in userworlds else '-',
        ]))

    @app.route('/level/save.html', methods=['POST'])
    def savemap():
        username = None
        sessionId = None
        mapId = None
        mapLength = None
        mapName = None

        nullcount = 0
        lastNull = 0

        user = None

        try:
            requestData = request.stream.read()

            username_length = int.from_bytes(requestData[1 : 2], byteorder='big')
            username = requestData[2 : 2 + username_length]
            sessionId_length = int.from_bytes(requestData[2 + username_length + 0 : 2 + username_length + 2], byteorder='big')
            sessionId = requestData[2 + username_length + 2 : 2 + username_length + 2 + sessionId_length]
            mapName_length = int.from_bytes(requestData[2 + username_length + 2 + sessionId_length + 1 : 2 + username_length + 2 + sessionId_length + 2], byteorder='big')
            mapName = requestData[2 + username_length + 2 + sessionId_length + 2 : 2 + username_length + 2 + sessionId_length + 2 + mapName_length]
            mapId = requestData[2 + username_length + 2 + sessionId_length + 2 + mapName_length]
            mapLength = int.from_bytes(requestData[2 + username_length + 2 + sessionId_length + 2 + mapName_length + 1 : 2 + username_length + 2 + sessionId_length + 2 + mapName_length + 1 + 4], byteorder='big')
            mapData = requestData[2 + username_length + 2 + sessionId_length + 2 + mapName_length + 1 + 4 : len(requestData)]

            username = str(utf8m_to_utf8s(username), 'utf-8')
            sessionId = str(utf8m_to_utf8s(sessionId), 'utf-8')
            mapName = str(utf8m_to_utf8s(mapName), 'utf-8')

            version = 2 if mapData[0:2] == bytes([0x1F, 0x8B]) else 1

        except:
            return Response("Something went wrong!", 500)

        userworlds = mongo.db.userworlds.find_one({"username" : username})

        if (userworlds == None):
            try:
                mongo.db.userworlds.insert_one({
                    "username": username,
                    (str(mapId)): {
                        "name": mapName,
                        "length": mapLength,
                        "data": mapData,
                        "createdAt": datetime.utcnow(),
                        "version" : version
                    }
                })
            except:
                return Response("Failed to save data.", 500)
        else:
            try:
                mongo.db.userworlds.update_one({"_id": userworlds["_id"]}, { "$set": { (str(mapId)): {
                    "name": mapName,
                    "length": mapLength,
                    "data": mapData,
                    "createdAt": datetime.utcnow(),
                    "version" : version
                } } })
            except:
                return Response("Failed to save data.", 500)

        return Response("ok")

    #classic
    @app.route('/level/load.html')
    def loadmap():
        username = request.args['user']
        mapId = request.args['id']

        try:
            userworlds = mongo.db.userworlds.find_one({"username" : username})
        except:
            return Response("User not found.", 404)

        if mapId in userworlds:
            response = Response(bytes([0x00, 0x02, 0x6F, 0x6B]) + userworlds[mapId]['data'], mimetype='application/x-mine')
            return response

        return Response("Map not found.", 404)