import codecs
from flask import request, abort, redirect, render_template, send_from_directory, Markup
import os
from markdown import markdown
from bson.objectid import ObjectId

readme_html = None
static_folder = None
mongo = None

def serve(path):
    global static_folder
    global mongo
    global readme_html

    path = path.replace(".jsp", "")
    path = path.replace("/resources/", "/MinecraftResources/")

    if path == "":
        return abort(404)

    # if not request.is_secure:
    #     return redirect(request.url.replace('http://', 'https://'))

    if os.path.exists("templates/public/" + path + ".html"):
        return render_template("public/" + path + ".html", readme_html=readme_html, args=request.args)
    elif os.path.exists(static_folder + '/' + path):
        return send_from_directory(static_folder, path)

    return abort(404)

def register_routes(app, _mongo):
    global readme_html
    global static_folder
    global mongo

    # These are imported after serve is defined.
    from routes.legacy import register_routes as register_legacy_routes
    from routes.mineonline import register_routes as register_mineonline_routes

    register_legacy_routes(app, _mongo)
    register_mineonline_routes(app, _mongo)

    readme_file = codecs.open("README.md", mode="r", encoding="utf-8")
    readme_html = Markup(markdown(readme_file.read()))
    readme_file.close()
    static_folder = app.static_folder
    mongo = _mongo

    @app.route('/', defaults={'path': 'index'})
    @app.route('/<path:path>')
    def serveroute(path):
        return serve(path)