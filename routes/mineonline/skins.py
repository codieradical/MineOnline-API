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
    @app.route('/api/player/<uuid>/skin/metadata', methods=['GET'])
    def mojangskinmetadata(uuid):
        uuid = str(UUID(uuid))
        try:
            profile = json.loads(requests.get("https://sessionserver.mojang.com/session/minecraft/profile/" + uuid).content)
            slim = json.loads(base64.b64decode(profile["properties"][0]["value"]))["textures"]["SKIN"]["metadata"]["model"] == "slim"
            return make_response(json.dumps({
                "slim": slim
            }))
        except:
            pass
        return make_response(json.dumps({
            "slim": True
        }))

    @app.route('/api/player/<uuid>/skin', methods=['GET'])
    def mojangskin(uuid):
        try:
            profile = json.loads(requests.get("https://sessionserver.mojang.com/session/minecraft/profile/" + uuid).content)
            skinUrl = json.loads(base64.b64decode(profile["properties"][0]["value"]))["textures"]["SKIN"]["url"]
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
            return abort(404)

    @app.route('/api/player/<uuid>/skin', methods=['GET'])
    def mineonlineskin(uuid):
        uuid = str(UUID(uuid))
        try:
            user = mongo.db.users.find_one({ "uuid": uuid })
        except:
            return abort(404)

        if not user or not 'skin' in user or not user['skin']:
            return abort(404)


        skinBytes = BytesIO(user['skin'])
        skinBytes.flush()
        skinBytes.seek(0)
        skin = Image.open(skinBytes)

        [width, height] = skin.size

        # Convert 64x32 skins to 64x64
        if(height < 64):
            legacySkin = skin
            skin = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
            skin.paste(legacySkin, (0, 0))
            #skin = ImageOps.expand(skin, (0, 0, 0, 64 - height), (255, 255, 255, 0))
            leg = skin.crop((0, 16, 16, 32))
            arm = skin.crop((40, 16, 56, 32))
            skin.paste(leg, (16, 48))
            skin.paste(arm, (32, 48))
        else:
            skin = skin.crop((0, 0, 64, 64))

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


    @app.route('/api/player/<uuid>/skin/head', methods=['GET'])
    def mineonlineskinhead(uuid):
        uuid = str(UUID(uuid))
        try:
            user = mongo.db.users.find_one({ "uuid": uuid })
        except:
            return abort(404)

        if not user or not 'skin' in user or not user['skin']:
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

    @app.route('/api/player/<uuid>/cloak', methods=['GET'])
    def mojangcloak(uuid):
        try:
            profile = json.loads(requests.get("https://sessionserver.mojang.com/session/minecraft/profile/" + uuid).content)
            skinUrl = json.loads(base64.b64decode(profile["properties"][0]["value"]))["textures"]["CLOAK"]["url"]
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
            return abort(404)
