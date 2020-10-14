
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

        return Response("Not Yet Implemented", 500)

        # try:
        #     users = mongo.db.users
        #     user = users.find_one({"user" : username})
        # except:
        #     return Response("User not found.", 404)

        # if (user == None):
        #     return Response("User not found.", 404)

        # if 'maps' in user:
        #     maps = user['maps']
        # else:
        #     return Response("-;-;-;-;-")

        # return Response(';'.join([
        #     maps['0']['name'] if '0' in maps else '-',
        #     maps['1']['name'] if '1' in maps else '-',
        #     maps['2']['name'] if '2' in maps else '-',
        #     maps['3']['name'] if '3' in maps else '-',
        #     maps['4']['name'] if '4' in maps else '-',
        # ]))

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
            sessionId_length = int.from_bytes(requestData[2 + username_length + 1 : 2 + username_length + 2], byteorder='big')
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

        return Response("Not Yet Implemented", 500)

        # try:
        #     users = mongo.db.users
        #     user = users.find_one({"user" : username, "sessionId": ObjectId(sessionId)})
        # except:
        #     return Response("Invalid Session", 401)

        # if (user == None):
        #     return Response("Invalid Session", 401)

        # try:
        #     users.update_one({"_id": user["_id"]}, { "$set": { ("maps." + str(mapId)): {
        #         "name": mapName,
        #         "length": mapLength,
        #         "data": mapData,
        #         "createdAt": datetime.utcnow(),
        #         "version" : version
        #     } } })
        # except:
        #     return Response("Failed to save data.", 500)

        # return Response("ok")

    #classic
    @app.route('/level/load.html')
    def loadmap():
        username = request.args['user']
        mapId = request.args['id']
        maps = None

        return Response("Not Yet Implemented", 500)

        # try:
        #     users = mongo.db.users
        #     user = users.find_one({"user" : username})
        # except:
        #     return Response("User not found.", 404)

        # if (user == None):
        #     return Response("User not found.", 404)

        # if 'maps' in user:
        #     maps = user['maps']
        # else:
        #     return Response("Map not found.", 404)

        # if mapId in maps:
        #     response = Response(bytes([0x00, 0x02, 0x6F, 0x6B]) + maps[mapId]['data'], mimetype='application/x-mine')
        #     return response