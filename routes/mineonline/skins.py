from flask import Response, request, make_response, abort
import json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
from uuid import uuid4, UUID
from utils.modified_utf8 import utf8m_to_utf8s, utf8s_to_utf8m
from PIL import Image, PngImagePlugin, ImageOps
from io import BytesIO, StringIO
import requests
import base64
from datetime import date

def register_routes(app, mongo):
    @app.route('/api/player/<uuid>/customcape', methods=['GET'])
    def customcloak(uuid):
        try:
            # Fetch from minecraftcapes
            profile = json.loads(requests.get("https://minecraftcapes.net/profile/" + uuid).content)
            return Response(base64.b64decode(profile["textures"]["cape"]))
        except Exception as e:
            return abort(404)

    @app.route('/api/player/<uuid>/eventcape', methods=['GET'])
    def eventcloak(uuid):
        if (date.today().day == 24 or date.today().day == 25) and date.today().month == 12:
            return Response("https://mineonline.codie.gg/MinecraftCloaks/xmas2010.png")

        if date.today().day == 31 and date.today().month == 12 and date.today().year == 2020:
            return Response("https://mineonline.codie.gg/MinecraftCloaks/newyear2021.png")

        if uuid == "7a8218cb88524ae1b79fa915a255a62a":
            return Response("https://mineonline.codie.gg/MinecraftCloaks/codieradical.png")

        return abort(404)
    
    @app.route('/api/playerhead', methods=['GET'])
    def playerHead():
        if not "user" in request.args:
            return abort(404)
        
        try:
            user = mongo.db.users.find_one({ "user": request.args["user"] })
        except:
            return abort(404)

        if not user:
            try:
                skinUrl = "https://minotar.net/avatar/" + request.args["user"]  + "/8"
                skinBytes = BytesIO(requests.get(skinUrl).content)
                skinBytes.flush()
                skinBytes.seek(0)

                response = Response(skinBytes.read(), mimetype="image/png")
                
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                response.headers['Cache-Control'] = 'public, max-age=0'

                return response
            except Exception as e:
                print(e)
                abort(404)

        if not 'skin' in user or not user['skin']:
            return abort(404)


        skinBytes = BytesIO(user['skin'])
        skinBytes.flush()
        skinBytes.seek(0)
        skin = Image.open(skinBytes)

        [width, height] = skin.size

        skin = skin.crop((8, 8, 16, 16))

        croppedSkin = BytesIO()
        skin.save(croppedSkin, "PNG")
        skinBytes.flush()
        croppedSkin.seek(0)

        response = Response(croppedSkin.read(), mimetype="image/png")
        
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers['Cache-Control'] = 'public, max-age=0'

        return response
