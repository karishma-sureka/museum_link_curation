from flask import Flask, render_template, request, url_for, jsonify, redirect, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient, ReturnDocument, ASCENDING, DESCENDING
from unidecode import unidecode

devmode = True

if devmode:
    server = "http://localhost:5000/"
    dbC = MongoClient('localhost', 27017)
else:
    server = "http://52.37.251.245/"
    #server = "http://ec2-52-37-251-245.us-west-2.compute.amazonaws.com/"
    #server = "http://linkcuration.ddns.net/"
    dbC = MongoClient('localhost', 12345)

# Flask configuration
app = Flask(__name__)

# restful, usrdb and login_manager instance
api = Api(app)
usrdb = SQLAlchemy(app)
lm = LoginManager(app)

lm.login_view = 'index'
lm.session_protection = 'strong'
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

confidenceLevel = 2
dname = "linkVerification"

if devmode:
    app.config['OAUTH_CREDENTIALS'] = {
        'facebook': {
            'id': '622058264638304',
            'secret': '56bba85a0bef4cae8d07537701bbfe1f'
        }
    }
else:
    app.config['OAUTH_CREDENTIALS'] = {
        'facebook': {
            'id': '621200901380211',
            'secret': '0afb04701e956a3cf74ac876560e7041'
        }
    }