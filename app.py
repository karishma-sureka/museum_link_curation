# Set the path
import os, sys
from flask import Flask, render_template, request, jsonify
from flask.ext.mongoengine import MongoEngine
from restfulInterface import *

webapp = Flask(__name__)
webapp.config['MONGODB_DB'] = 'Link_Curation_Interface'
webapp.config['MONGODB_HOST'] = '127.0.0.1'
webapp.config["SECRET_KEY"] = "KeepThisS3cr3t"
webapp.config['DEBUG_TB_PANELS'] = ['flask.ext.mongoengine.panels.MongoDebugPanel']

db = MongoEngine(webapp)

#MongoEngine.connect(db=curation,alias='default')
#MongoEngine.register_connection('default', port=12345)

@webapp.route('/')
def indexPage():
    clearData()
    populateData()
    if request.method == 'POST':
        session['username'] = request.form['username']
        print request.form['username']
        return redirect(url_for('index'))
    return render_template('index.html')

@webapp.route('/get-q', methods=['POST'])
def rest_get_question():
    # Bad input conditions
    if not request.json:
        abort(400)
    if not 'uid' in request.json:
        abort(400)
        
    q = get_question(request.json['uid'])
    return jsonify({'qid':q.qid,'uri1':q.uri1,'uri2':q.uri2}), 201
   
@webapp.route('/submit-a', methods=['POST'])
def rest_submit_answer():
    # Bad input conditions
    if not request.json:
        abort(400)
    if not 'qid' in request.json:
        abort(400)
    if not 'uid' in request.json: # link to Answer.curator
        abort(400)
    if not 'answer' in request.json: # Answer.value (# 1 - Yes, 2 - No, 3 - Not Sure)
        abort(400)
       
    if not 'comment' in request.json:
        #ans = Answer(value=request.json['answer'],comment="",author=Curator.objects(uid=uid))
        ans = Answer(value=request.json['answer'],comment="",author=Curator(uid="nilayvac@usc.edu",name="Nilay Chheda",rating=5))
    else:
        #ans = Answer(value=request.json['answer'],comment=request.json['comment'],author=Curator.objects(uid=uid))
        ans = Answer(value=request.json['answer'],comment=request.json['comment'],author=Curator(uid="nilayvac@usc.edu",name="Nilay Chheda",rating=5))
        
    a = submit_answer(request.json['qid'],ans)
    return jsonify({'answerSubmitted':a.value,'comment':a.comment,'Author':a.author.name}), 201
   
@webapp.route('/user/<username>')
def show_user_profile(username):
    return 'Welcome %s' % username
    
@webapp.route('/clear')
def clearDb():
    clearData()

@webapp.route('/reset')
def resetDb():
    populateData()
    
if __name__ == "__main__":
    webapp.run(debug=True)