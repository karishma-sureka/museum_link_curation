from flask import Flask, render_template, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from dbMgr import *
from pprint import pprint

webapp = Flask(__name__)
api = Api(webapp)
dbClient = MongoClient('localhost', 27017)
dbName = "TestDb1"

# Uncommment below lines only once
cleanDatabases(dbClient,dbName)
createDatabase(dbClient,dbName)
cleanDatabase(dbClient,dbName,"answer")
printDatabases(dbClient,dbName)

# Handle RESTful API for submitting answer
class answers(Resource):
    def put(self):
        print "Input received: ",request.json
        # Input validation
        if not 'comment' in request.json:
            a_comment = "No Comment Provided"
        else:
            a_comment = request.json['comment']
            
        if not 'value' in request.json:
            return {'status': 400, 'message': 'value not provided with ther request'}
        if not 'qid' in request.json:
            return {'status': 400, 'message': 'qid not provided with ther request'}
        if not 'uid' in request.json:
            return {'status': 400, 'message': 'uid not provided with ther request'}
        a_value = request.json['value']
        qid = request.json['qid']
        uid = request.json['uid']
        
        answer = {"value":a_value,
          "comment":a_comment,
          "author":"nilayvac@usc.edu"
         }
        return {'Status':submitAnswer(dbClient,dbName,qid,answer,uid)}
        
# Handle RESTful API for getting/submitting questions
class questions(Resource):
    def get(self):
        print "Input received: ",request.json
         
        # Request coming from dedupe
        if not 'uid' in request.json:
            
            # dedupe sending just one pair
            if not 'bulk' in request.json:
                if not 'uri1' in request.json:
                    return {'status': 400, 'message': 'uri1 not provided with ther request'}
                if not 'uri2' in request.json:
                    return {'status': 400, 'message': 'uri2 not provided with ther request'}
                if not 'dedupe' in request.json:
                    return {'status': 400, 'message': 'dedupe not provided with ther request'}
                
                uri1 = request.json['uri1']
                uri2 = request.json['uri2']
                dedupe = request.json['dedupe']
                
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
                for i in range(0,request.json['bulk']):
                    payload = request.json['payload'][i]
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
        # request coming from the interface
        else:
            uid = request.json['uid']
            
            if not 'bulk' in request.json:
                count = 1
            else:
                count = request.json['bulk']
            
            if not 'stats' in request.json:
                stats = False
            else:
                stats = request.json['stats']

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
        
# class homepage(Resource):
    # def get(self):
        # return render_template('cards.html')

# api.add_resource(homepage, '/v1/')
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
