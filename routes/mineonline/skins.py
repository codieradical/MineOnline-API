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

def register_routes(app, mongo):
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
