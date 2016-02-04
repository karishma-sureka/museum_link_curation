# Set the path
import os, sys
from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_debugtoolbar import DebugToolbarExtension

webapp = Flask(__name__)
webapp.debug = True
webapp.config['MONGODB_DB'] = 'Link_Curation_Interface'
webapp.config['MONGODB_HOST'] = '127.0.0.1'
webapp.config["SECRET_KEY"] = "KeepThisS3cr3t"
webapp.config['DEBUG_TB_PANELS'] = ['flask.ext.mongoengine.panels.MongoDebugPanel']
db = MongoEngine(webapp)
webapp.session_interface = MongoEngineSessionInterface(db)
toolbar = DebugToolbarExtension(webapp)

@webapp.route("/")
def main():
    return render_template('index.html')

if __name__ == "__main__":
    webapp.run()