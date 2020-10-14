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
import jwt

def register_routes(app, mongo):
    @app.route('/api/stub/ok')
    def stubok():
        return Response("ok")






