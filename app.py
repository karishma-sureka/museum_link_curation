from flask import Flask, render_template, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from dbMgr import *

webapp = Flask(__name__)
api = Api(webapp)
dbClient = MongoClient('localhost', 27017)
dbName = "TestDb1"

# Uncommment below lines only once
cleanDatabase(dbClient,dbName)
createDatabase(dbClient,dbName)
#printDatabase(dbClient,dbName)

# Global variables
qid = 0
aid = 0
comment = "Default comment"

class answers(Resource):
    def put(self):
        # Input validation
        if not 'comment' in request.form:
            a_comment = "No Comment Provided"
        else:
            a_comment = request.form['comment']
            
        if not 'value' in request.form:
            return {'status': 400, 'message': 'value not provided with ther request'}
        if not 'qid' in request.form:
            return {'status': 400, 'message': 'qid not provided with ther request'}
        a_value = request.form['value']
        qid = request.form['qid']
        
        answer = {"value":a_value,
          "comment":a_comment,
          "author":"dakldsjkaldjoi3uoiuje3kl2knkjn" # Random string, Get object ID of curator
         }
        submitAnswer(dbClient,dbName,qid,answer)
        return {'qid':qid,'author':answer['author'],'value':answer['value'],'comment':answer['comment']}
    
    def get(self):
        return {'comment':comment,'qid':qid, 'aid':aid}
        
class questions(Resource):
    def get(self):
        question = getQuestion(dbClient,dbName,"nilayvac@usc.edu")
        return {'qid': str(question['_id']),"uri1":question['uri1'],"uri2":question['uri2']}
        
        #from flask import jsonify # jsonify usage
        #return jsonify({'answerSubmitted':a.value,'comment':a.comment,'Author':a.author.name}), 201

class homepage(Resource):
    def get(self):
        return render_template('index.html')

api.add_resource(homepage, '/v1/')
api.add_resource(answers, '/v1/answer')
api.add_resource(questions, '/v1/question')

@webapp.route('/')
def indexPage():
    # if request.method == 'POST':
        # session['username'] = request.form['username']
        # print request.form['username']
        # return redirect(url_for('index'))
    return render_template('cards.html')
   
@webapp.route('/user/<username>')
def show_user_profile(username):
    return 'Welcome %s' % username
        
if __name__ == "__main__":
    webapp.run(debug=True)
