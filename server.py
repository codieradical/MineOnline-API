from flask import Flask, Response, request, send_from_directory, abort, send_file, render_template, redirect, url_for, make_response, Markup, jsonify
from flask_uuid import FlaskUUID
import json
import os
import bcrypt
import re
from flask_pymongo import PyMongo
from pymongo import IndexModel, ASCENDING, DESCENDING, errors
from bson import json_util
from bson.objectid import ObjectId
from utils.modified_utf8 import utf8m_to_utf8s, utf8s_to_utf8m
from datetime import datetime
import hashlib
import codecs
from PIL import Image, PngImagePlugin, ImageOps
from io import BytesIO, StringIO
from uuid import uuid4, UUID
import base64
import time
import sys
import glob
from utils.servers import *
from utils.versions import load_versions
import routes

# import config if present
try: import config
except: pass

app = Flask(__name__,
            static_folder='public/',
            template_folder='templates')
            
FlaskUUID(app)

app.config['MONGO_DBNAME'] = os.getenv("MONGO_DBNAME")
app.config['MONGO_URI'] = os.getenv("MONGO_URI")
secretkey = os.getenv("SECRET_KEY")
app.secret_key = secretkey

app.config.update(dict(
    DEBUG = False,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = os.getenv("EMAIL_USER"),
    MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD"),
))



mongo = PyMongo(app)
mongo.db.serverjoins.create_index( "createdAt", expireAfterSeconds = 600 )

load_versions()

routes.register_routes(app, mongo)