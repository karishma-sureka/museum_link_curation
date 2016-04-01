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
        #print "Input received: ",request.json
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
        
        answer = {"value":a_value,
          "comment":a_comment,
          "author":"nilayvac@usc.edu" # Random string, Get object ID of curator or from session oauth
         }
        return {'Status':submitAnswer(dbClient,dbName,qid,answer)}
        
# Handle RESTful API for getting/submitting questions
class questions(Resource):
    def get(self):
        print "Input received: ",request.json
         
        # Request coming from dedup
        if not 'uid' in request.json:
            
            # dedup sending just one pair
            if not 'bulk' in request.json:
                if not 'uri1' in request.json:
                    return {'status': 400, 'message': 'uri1 not provided with ther request'}
                if not 'uri2' in request.json:
                    return {'status': 400, 'message': 'uri2 not provided with ther request'}
                if not 'dedup' in request.json:
                    return {'status': 400, 'message': 'dedup not provided with ther request'}
                
                uri1 = request.json['uri1']
                uri2 = request.json['uri2']
                dedup = request.json['dedup']
                
                decision = addOrUpdateQuestion(dbClient,dbName,uri1,uri2,dedup)
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
            
            # Dedup sending multiple pairs
            else:
                bulkOutput = []
                for i in range(0,request.json['bulk']):
                    if not 'uri1' in request.json:
                        return {'status': 400, 'message': 'uri1 not provided with ther request'}
                    if not 'uri2' in request.json:
                        return {'status': 400, 'message': 'uri2 not provided with ther request'}
                    if not 'dedup' in request.json:
                        return {'status': 400, 'message': 'dedup not provided with ther request'}
                    
                    uri1 = request.json['uri1']
                    uri2 = request.json['uri2']
                    dedup = request.json['dedup']
                    
                    decision = addOrUpdateQuestion(dbClient,dbName,uri1,uri2,dedup)
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
        else:
            uid = request.json['uid']
            questions = getQuestionsForUID(dbClient,dbName,uid)
            if questions != None:
                output = []
                for question in questions:                
                    left = dbClient[dbName]["artists"].find_one({'@id':question['uri1']},projection={'_id':False})
                    right = dbClient[dbName]["artists"].find_one({'@id':question['uri2']},projection={'_id':False})
                    #print "\nLeft\n  ",left
                    #print "\nRight\n ",right
                    matches = getMatches(left, right)
                    #print "\nmatches :\n"
                    #pprint(matches)
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
