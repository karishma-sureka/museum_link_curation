import os
from flask import Flask, render_template, request, g, url_for, jsonify, redirect
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from pymongo import MongoClient
from pprint import pprint
from dbMgr import *

webapp = Flask(__name__)
api = Api(webapp)
# On Server
# dbClient = MongoClient('localhost', 12345)
dbClient = MongoClient('localhost', 27017)
dbName = "TestDb1"
usrdb = SQLAlchemy(webapp)
auth = HTTPBasicAuth()
webapp.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
webapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
webapp.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
tokenExpiry = 600 # 60 seconds X 10

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

@webapp.route('/spec')
def show_specs():
    return render_template('spec.html')
    
@webapp.route('/answer')
def redirectAnswer():
    return redirect(url_for("answer"))
    
@webapp.route('/question')
def redirectQuestion():
    return redirect(url_for("question"))

@webapp.route('/user')
def redirectUser():
    return redirect(url_for("user"))

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
            return {'message': 'value not provided with ther request'}, 400
        if not 'qid' in request.json:
            return {'message': 'qid not provided with ther request'}, 400
        
        a_value = request.json['value']
        qid = request.json['qid']
        uid = g.user.username
        answer = {"value":a_value,"comment":a_comment,"author":uid}
        
        rsp = submitAnswer(dbClient,dbName,qid,answer,uid)
        if rsp["status"] == False:
            return {'message':rsp["message"]},400
        else:
            return {'message':rsp["message"]}
        
# Handle RESTful API for getting/submitting questions
class questMgr(Resource):
    
    # Create questions from dedupe provided pairs
    def post(self):
        print "Input received: ",request.json
        
        if request.json == None:
            return {'message': 'No input provided'}, 400
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
            return {'message': 'No input provided'}, 400
        
        if not 'username' in request.json:
            return {'message': 'username not provided with ther request'}, 400
        if not 'password' in request.json:
            return {'message': 'password not provided with ther request'}, 400
            
        return register_user(request.json['username'],request.json['password'])

    # Login and get time bound token for API access
    def get(self):
        if request.json == None or not 'duration' in request.json:
            return login_user(tokenExpiry)
        else:
            return login_user(request.json['duration'])
            
    # Update User (Curator) profile. 
    @auth.login_required
    def put(self):
        print "Input received: ",request.json
        
        if request.json == None:
            return {'message': 'No input provided'}, 400
        
        # Update tag for a user
        if 'tags' in request.json:
            #print request.json["tags"], type(request.json["tags"])
            if type(request.json["tags"]) != list:
                return {'message': 'Tags type should by list of String'}, 400
                
            tags = []
            for tag in request.json['tags']:
                tags = tags + [dbClient[dbName]["tag"].find_one({'tagname':tag})["_id"]]
            dbClient[dbName]["curator"].find_one_and_update({'uid':g.user.username},{'$set': {'tags':tags}})
        
        # Update name of a user
        if 'name' in request.json:
            #print request.json["name"], type(request.json["name"])
            if type(request.json["name"]) != str and type(request.json["name"]) != unicode:
                return {'message': 'Name type should by String'}, 400
            dbClient[dbName]["curator"].find_one_and_update({'uid':g.user.username},{'$set': {'name':request.json["name"]}})
        
        # Update rating of a user
        if 'rating' in request.json:
            #print request.json["name"], type(request.json["name"])
            if type(request.json["rating"]) != int:
                return {'message': 'Rating type should by integer'}, 400
            if request.json["rating"] > 5 or request.json["rating"] < 0:
                return {'message': 'Rating should be between 0-5 only'}, 400
            dbClient[dbName]["curator"].find_one_and_update({'uid':g.user.username},{'$set': {'rating':request.json["rating"]}})
        
        u = dbClient[dbName]["curator"].find_one({'uid':g.user.username},projection={'_id':False})
        return {"username":u["uid"],"name":u["name"],"tags":getTags(dbClient,dbName,u),"rating":u["rating"]}
        
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

# Rest API endpoints (V1)
api.add_resource(ansMgr, '/v1/answer',endpoint='answer')
api.add_resource(questMgr, '/v1/question',endpoint='question')
api.add_resource(userMgr, '/v1/user',endpoint='user')
        
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
        return {'message': 'User does not exist'}, 400
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
        return {'message': 'User alrady exists'}, 400
                
    user = User(username=username)
    user.hash_password(password)
    usrdb.session.add(user)
    usrdb.session.commit()
    
    print "Added user with username:",user.username," and id:",user.id
    location = url_for('get_user', id=user.id, _external=True)
    
    # Add curator in mongodb. Name/tags/rating to be updated later with put request
    addCurator(dbClient,dbName,{"uid":username,"name":"","tags":[],"rating":5})
    
    #return {'status':201,'username':user.username,'Location': url_for('get_user', id=user.id, _external=True)}
    return {'username':user.username,'Location': url_for('get_user', id=user.id, _external=True)},201

@auth.login_required
def login_user(duration):
    token = g.user.generate_auth_token(duration)
    t = getTags(dbClient,dbName,dbClient[dbName]["curator"].find_one({'uid':g.user.username}))
    
    
    u = dbClient[dbName]["curator"].find_one({'uid':g.user.username},projection={'_id':False})
    u = {"username":u["uid"],"name":u["name"],"tags":getTags(dbClient,dbName,u),"rating":u["rating"]}
    
    #return jsonify('token':{'value': token.decode('ascii'), 'duration':duration},'user':u})
    return {'token':{'value': token.decode('ascii'), 'duration':duration},'user':u}
    
def createQuestionsFromPairs(jsonData):
    # dedupe sending just one pair
    if not 'bulk' in jsonData:
        if not 'uri1' in jsonData:
            return {'message': 'uri1 not provided with the request'}, 400
        if not 'uri2' in jsonData:
            return {'message': 'uri2 not provided with the request'}, 400
        if not 'dedupe' in jsonData:
            return {'message': 'dedupe not provided with the request'}, 400
        
        uri1 = jsonData['uri1']
        uri2 = jsonData['uri2']
        dedupe = jsonData['dedupe']
        
        decision = addOrUpdateQuestion(dbClient,dbName,uri1,uri2,dedupe)
        printDatabase(dbClient,dbName,"question")
        if decision != None:
            # Iterate over decision documts and send various comments and actual answer
            output = {"Value":[],"Comment":[]}
            for aid in decision:
                a = dbClient[dbName]["answer"].find_one({'_id':ObjectId(aid)})
                output["Value"] = output["Value"]+[a["value"]]
                output["Comment"] = output["Comment"]+[a["comment"]]
            return output
        else:
            return {'message':"Question does not have human curated information yet."}
    
    # dedupe sending multiple pairs
    else:
        bulkOutput = []
        for i in range(0,jsonData['bulk']):
            payload = jsonData['payload'][i]
            #print "\n Processing payload: ",payload
            if not 'uri1' in payload:
                return {'message': 'uri1 not provided with ther request'}, 400
            if not 'uri2' in payload:
                return {'message': 'uri2 not provided with ther request'}, 400
            if not 'dedupe' in payload:
                return {'message': 'dedupe not provided with ther request'}, 400
            
            uri1 = payload['uri1']
            uri2 = payload['uri2']
            dedupe = payload['dedupe']
            
            decision = addOrUpdateQuestion(dbClient,dbName,uri1,uri2,dedupe)
            printDatabase(dbClient,dbName,"question")
            if decision != None:
                # Iterate over decision documts and send various comments and actual answer
                output = {"Value":[],"Comment":""}
                for aid in decision:
                    a = dbClient[dbName]["answer"].find_one({'_id':ObjectId(aid)})
                    output["Value"] = output["Value"]+[a["value"]]
                    output["Comment"] = output["Comment"]+[a["Comment"]]
                bulkOutput = bulkOutput+[output]
            else:
                bulkOutput = bulkOutput+[{'message':'Question does not have human curated information yet.'}]
        return bulkOutput

@auth.login_required
def getQuestionsForUser(jsonData):

    if jsonData == None:
        count = 10
        stats = False
    else: 
        if not 'bulk' in jsonData:
            count = 10
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
            if checkURIOrdering(question['uri1'],question['uri2']):
                left = dbClient[dbName]["artists"].find_one({'@id':question['uri1']},projection={'_id':False})
                right = dbClient[dbName]["artists"].find_one({'@id':question['uri2']},projection={'_id':False})
                if left == None:
                    print "Couldn't retrive entity with URI", question['uri1']
                    continue
                if right == None:
                    print "Couldn't retrive entity with URI", question['uri2']
                    continue
            else:
                left = dbClient[dbName]["artists"].find_one({'@id':question['uri2']},projection={'_id':False})
                right = dbClient[dbName]["artists"].find_one({'@id':question['uri1']},projection={'_id':False})
                if left == None:
                    print "Couldn't retrive entity with URI", question['uri2']
                    continue
                if right == None:
                    print "Couldn't retrive entity with URI", question['uri1']
                    continue
                    
            #print "\nLeft\n  ",left 
            #print "\nRight\n ",right
            
            matches = getMatches(left, right)
            #print "\nmatches :\n"
            #pprint(matches)
            t = getTags(dbClient,dbName,question)
            if stats == "True":
                s = getStats(dbClient,dbName,question)
                output = output+[{'qid': str(question['_id']),"ExactMatch":matches["ExactMatch"],"Unmatched":matches['Unmatched'],"tags":t,"stats":s}]
            else:
                output = output+[{'qid': str(question['_id']),"ExactMatch":matches["ExactMatch"],"Unmatched":matches['Unmatched'],"tags":t}]
        return output
    else:
        return {'status':"Couldn't retrive questions mostly because user not found."}, 400
        
if __name__ == '__main__':
    # User account database
    usrdb.drop_all()
    usrdb.create_all()
    #if not os.path.exists('db.sqlite'):
        #usrdb.create_all()
    webapp.run(debug=True)
