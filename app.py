# Set the path
import os, sys
from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from dbMgr import *

#from flask.ext.mongoengine import MongoEngine
#from flask_restful_swagger import swagger
#from restfulInterface import *

webapp = Flask(__name__)
api = Api(webapp)
dbClient = MongoClient('localhost', 27017)
dbName = "TestDb1"

#cleanDatabase(dbClient,dbName)
#createDatabase(dbClient,dbName)
#printDatabase(dbClient,dbName)

# Global variables
qid = 0
aid = 0
comment = "Default comment"

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class answers(Resource):
    def put(self):
        qid = request.form['qid']
        aid = request.form['aid']
        comment = request.form['comment']
        return {'comment':comment,'qid':qid, 'aid':aid}
    
    def get(self):
        return {'comment':comment,'qid':qid, 'aid':aid}
        
class questions(Resource):
    def get(self):
        question = getQuestion(dbClient,dbName,"nilayvac@usc.edu")
        return {'qid': str(question['_id']),"uri1":question['uri1'],"uri2":question['uri2']}

api.add_resource(HelloWorld, '/v1/')
api.add_resource(answers, '/v1/answer')
api.add_resource(questions, '/v1/question')

@webapp.route('/')
def indexPage():
    if request.method == 'POST':
        session['username'] = request.form['username']
        print request.form['username']
        return redirect(url_for('index'))
    return render_template('index.html')

# @webapp.route('/get-q', methods=['POST'])
# def rest_get_question():
    # # Bad input conditions
    # if not request.json:
        # abort(400)
    # if not 'uid' in request.json:
        # abort(400)
        
    # return jsonify({'qid':q.qid,'uri1':q.uri1,'uri2':q.uri2}), 201
   
# @webapp.route('/submit-a', methods=['POST'])
# def rest_submit_answer():
    # # Bad input conditions
    # if not request.json:
        # abort(400)
    # if not 'qid' in request.json:
        # abort(400)
    # if not 'uid' in request.json: # link to Answer.curator
        # abort(400)
    # if not 'answer' in request.json: # Answer.value (# 1 - Yes, 2 - No, 3 - Not Sure)
        # abort(400)
       
    # if not 'comment' in request.json:
        # #ans = Answer(value=request.json['answer'],comment="",author=Curator.objects(uid=uid))
        # ans = Answer(value=request.json['answer'],comment="",author=Curator(uid="nilayvac@usc.edu",name="Nilay Chheda",rating=5))
    # else:
        # #ans = Answer(value=request.json['answer'],comment=request.json['comment'],author=Curator.objects(uid=uid))
        # ans = Answer(value=request.json['answer'],comment=request.json['comment'],author=Curator(uid="nilayvac@usc.edu",name="Nilay Chheda",rating=5))
        
    # a = submit_answer(request.json['qid'],ans)
    # return jsonify({'answerSubmitted':a.value,'comment':a.comment,'Author':a.author.name}), 201
   
@webapp.route('/user/<username>')
def show_user_profile(username):
    return 'Welcome %s' % username
        
if __name__ == "__main__":
    webapp.run(debug=True)