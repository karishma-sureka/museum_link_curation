import os
from flask import Flask, render_template, request, g, url_for, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from pymongo import MongoClient
from pprint import pprint
from dbMgr import *
#from usrMgr import *

webapp = Flask(__name__)
api = Api(webapp)
dbClient = MongoClient('localhost', 27017)
dbName = "TestDb1"
usrdb = SQLAlchemy(webapp)
auth = HTTPBasicAuth()
webapp.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
webapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
webapp.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
tokenExpiry = 60 # 60 seconds

# Database of curation data
# Uncommment below lines only once
cleanDatabases(dbClient,dbName)
createDatabase(dbClient,dbName)
cleanDatabase(dbClient,dbName,"answer")
printDatabases(dbClient,dbName)

@webapp.route('/curation')
def submit():
    return render_template('cards.html')

@webapp.route('/')
def show_login_profile():
    return render_template('login.html')

# Handle RESTful API for submitting answer
class ansMgr(Resource):
    
    @auth.login_required
    def put(self):
        print "Input received: ",request.json
        
        if request.json == None:
            return {'status': 400, 'message': 'No input provided'}
        
        # Input validation
        if not 'comment' in request.json:
            a_comment = "No Comment Provided"
        else:
            a_comment = request.json['comment']
            
        if not 'value' in request.json:
            return {'status': 400, 'message': 'value not provided with ther request'}
        if not 'qid' in request.json:
            return {'status': 400, 'message': 'qid not provided with ther request'}
        
        a_value = request.json['value']
        qid = request.json['qid']
        uid = g.user.username
        answer = {"value":a_value,"comment":a_comment,"author":uid}
        
        return {'Status':submitAnswer(dbClient,dbName,qid,answer,uid)}
        
# Handle RESTful API for getting/submitting questions
class questMgr(Resource):
    
    # Create questions from dedupe provided pairs
    def post(self):
        print "Input received: ",request.json
        
        if request.json == None:
            return {'status': 400, 'message': 'No input provided'}
        else:
            return createQuestionsFromPairs(request.json)
    
    def get(self):
        print "Input received: ",request.json
        
        if request.json == None:
            return getQuestionsForUser(None)
        else:
            return getQuestionsForUser(request.json)

# Handle RESTful API for user services like  Registration/Login/Logout/Statistics
class userMgr(Resource):
    
    # Register User
    def post(self):
        print "Input received: ",request.json
        
        if request.json == None:
            return {'status': 400, 'message': 'No input provided'}
        
        if not 'username' in request.json:
            return {'status': 400, 'message': 'username not provided with ther request'}
        if not 'password' in request.json:
            return {'status': 400, 'message': 'password not provided with ther request'}
            
        return register_user(request.json['username'],request.json['password'])

    # Login and get time bound token for API access
    def get(self):
        if not 'duration' in request.json:
            return login_user(tokenExpiry)
        else:
            return login_user(request.json['duration'])
        
# Rest API endpoints
api.add_resource(ansMgr, '/v1/answer')
api.add_resource(questMgr, '/v1/question')
api.add_resource(userMgr, '/v1/user')

# User Class definitio for SQLAlchemy object
class User(usrdb.Model):
    __tablename__ = 'users'
    id = usrdb.Column(usrdb.Integer, primary_key=True)
    username = usrdb.Column(usrdb.String(32), index=True)
    password_hash = usrdb.Column(usrdb.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=tokenExpiry):
        s = Serializer(webapp.config['SECRET_KEY'], expires_in=expiration)
        #return s.dumps(0,header_fields={'id': self.id})
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(webapp.config['SECRET_KEY'])
        try:
            #data = s.loads(token,return_header=True)
            data = s.loads(token)
            print data
        except SignatureExpired:
            #print "Token Expired"
            return None    # valid token, but expired
        except BadSignature:
            #print "Token Invalid"
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@webapp.route('/v1/user/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        return {'status': 400, 'message': 'User does not exist'}
    return jsonify({'username': user.username})

@webapp.route('/v1/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(tokenExpiry)
    return jsonify({'token': token.decode('ascii'), 'duration': tokenExpiry})

@webapp.route('/v1/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

def register_user(username,password):
    if User.query.filter_by(username=username).first() is not None:
        return {'status': 400, 'message': 'User alrady exists'}
                
    user = User(username=username)
    user.hash_password(password)
    usrdb.session.add(user)
    usrdb.session.commit()
    
    print "Added user with username:",user.username," and id:",user.id
    location = url_for('get_user', id=user.id, _external=True)
    
    return {'status':201,'username':user.username,'Location': url_for('get_user', id=user.id, _external=True)}

@auth.login_required
def login_user(duration):
    token = g.user.generate_auth_token(duration)
    return jsonify({'token': token.decode('ascii'), 'duration (in seconds)': duration})
    
def createQuestionsFromPairs(jsonData):
    # dedupe sending just one pair
    if not 'bulk' in jsonData:
        if not 'uri1' in jsonData:
            return {'status': 400, 'message': 'uri1 not provided with the request'}
        if not 'uri2' in jsonData:
            return {'status': 400, 'message': 'uri2 not provided with the request'}
        if not 'dedupe' in jsonData:
            return {'status': 400, 'message': 'dedupe not provided with the request'}
        
        uri1 = jsonData['uri1']
        uri2 = jsonData['uri2']
        dedupe = jsonData['dedupe']
        
        decision = addOrUpdateQuestion(dbClient,dbName,uri1,uri2,dedupe)
        printDatabase(dbClient,dbName,"question")
        if decision != None:
            # Iterate over decision documts and send various comments and actual answer
            output = {"aValue":[],"aComment":[]}
            for aid in decision:
                a = dbClient[dbName]["answer"].find_one({'_id':ObjectId(aid)})
                output["aValue"] = output["aValue"]+[a["value"]]
                output["aComment"] = output["aComment"]+[a["comment"]]
            return output
        else:
            return {'status':"Question does not have human curated information yet."}
    
    # dedupe sending multiple pairs
    else:
        bulkOutput = []
        for i in range(0,jsonData['bulk']):
            payload = jsonData['payload'][i]
            #print "\n Processing payload: ",payload
            if not 'uri1' in payload:
                return {'status': 400, 'message': 'uri1 not provided with ther request'}
            if not 'uri2' in payload:
                return {'status': 400, 'message': 'uri2 not provided with ther request'}
            if not 'dedupe' in payload:
                return {'status': 400, 'message': 'dedupe not provided with ther request'}
            
            uri1 = payload['uri1']
            uri2 = payload['uri2']
            dedupe = payload['dedupe']
            
            decision = addOrUpdateQuestion(dbClient,dbName,uri1,uri2,dedupe)
            printDatabase(dbClient,dbName,"question")
            if decision != None:
                # Iterate over decision documts and send various comments and actual answer
                output = {"aValue":[],"aComment":""}
                for aid in decision:
                    a = dbClient[dbName]["answer"].find_one({'_id':ObjectId(aid)})
                    output["aValue"] = output["aValue"]+[a["value"]]
                    output["aComment"] = output["aComment"]+[a["aComment"]]
                bulkOutput = bulkOutput+[output]
            else:
                bulkOutput = bulkOutput+[{'status':'Question does not have human curated information yet.'}]
        return bulkOutput

@auth.login_required
def getQuestionsForUser(jsonData):

    if jsonData == None:
        count = 1
        stats = False
    else: 
        if not 'bulk' in jsonData:
            count = 1
        else:
            count = jsonData['bulk']
        
        if not 'stats' in jsonData:
            stats = False
        else:
            stats = jsonData['stats']

    uid = g.user.username
    questions = getQuestionsForUID(dbClient,dbName,uid,count)
    if questions != None:
        output = []
        for question in questions:
            #print question
            left = dbClient[dbName]["artists"].find_one({'@id':question['uri1']},projection={'_id':False})
            right = dbClient[dbName]["artists"].find_one({'@id':question['uri2']},projection={'_id':False})
            #print "\nLeft\n  ",left 
            #print "\nRight\n ",right
            matches = getMatches(left, right)
            #print "\nmatches :\n"
            #pprint(matches)
            if stats == "True":
                s = getStats(dbClient,dbName,question)
                output = output+[{'qid': str(question['_id']),"ExactMatch":matches["ExactMatch"],"Unmatched":matches['Unmatched'],"stats":s}]
            else:
                output = output+[{'qid': str(question['_id']),"ExactMatch":matches["ExactMatch"],"Unmatched":matches['Unmatched']}]
        return output
    else:
        return {'status':"Couldn't retrive questions"}
        
if __name__ == '__main__':
    # User account database
    usrdb.drop_all()
    usrdb.create_all()
    #if not os.path.exists('db.sqlite'):
        #usrdb.create_all()
    webapp.run(debug=True)
