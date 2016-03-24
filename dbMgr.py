import datetime
from random import randint
import csv
from pymongo import MongoClient

confedenceLevel = 2
contrastLevel = 2

# Print the database just to check current data
def printDatabase(dbC,dname):
    print "Printing ",dname," if it exists"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "Collection ",cname
        for val in dbC[dname][cname].find():
            print " Document ", val

# Removes all the data from all tables of given database
def cleanDatabase(dbC,dname):
    print "Dropping database",dname,"if it exists"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "Dropping collection (aka database)",cname
        for val in dbC[dname][cname].find():
            print val
        dbC[dname][cname].delete_many({})
        dbC[dname][cname].drop()
        
# Create database with default values for curation
def createDatabase(dbC,dname):
    populateTags(dbC,dname)
    populateCurators(dbC,dname)
    #populateQuestions(dbC,dname)
    populateQuestionsFromCSV(dbC,dname,'sample.csv')
    
    # Not required to be populated
    # Save on the fly as per the PUT request 
    #saveAnswers(dbC,dname) 
    
    #populateRefURI(dbC,dname)
    
#Tag
    #tagname, string 
# Populate database with default tags
def populateTags(dbC,dname):
    t = dbC[dname]["tag"]
    te = {"tagname":"randomtag1"}
    t.insert_one(te)
    te = {"tagname":"randomtag2"}
    t.insert_one(te)
    te = {"tagname":"randomtag3"}
    t.insert_one(te)
    te = {"tagname":"randomtag4"}
    t.insert_one(te)
    te = {"tagname":"randomtag5"}
    t.insert_one(te)
    te = {"tagname":"randomtag6"}
    t.insert_one(te)
    
#Curator
    #uid, String - userID
    #name, String
    #rating, Integer
    #questionsSeen, List of object IDs from Question
    #tags, list of object IDs from Tags
    
# Populate database with default curators
def populateCurators(dbC,dname):
    c = dbC[dname]["curator"]
    ce = {"uid":"nilayvac@usc.edu",
          "name":"Nilay Chheda",
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag1"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag4"})],
          "rating":5}
    c.insert_one(ce)
    ce = {"uid":"ksureka@usc.edu",
          "name":"Karishma Sureka",
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
          "rating":5}
    c.insert_one(ce)

# Add the new curator from the client interface
def addCurator(dbC, dname, ce):
    c = dbC[dname]["curator"]
    c.insert_one(ce)
    
# Question
    #status, integer: 1 - Not Started, 2 - In Progress, 3 - Completed, 4 - Disagreement
    #lastSeen, datetime field to select question based on time it was asked to previous curator
    #tags, list of object IDs from Tags
    #uri1, for now, just a URI related to a specific artist
    #uri2, for now, just another URI related to same specific artist
    #decision, list of object IDs from Answer
    
# Populate default set of questions
def populateQuestions(dbC,dname):
    q = dbC[dname]["question"]
    
    qe = {"status":1,
          "lastSeen": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag1"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag4"})],
           "uri1":"http://vocab.getty.edu/ulan/500028092",
           "uri2":"http://edan.si.edu/saam/id/person-institution/1681",
           "decision": [] #Should be updated in submit answer
         }
    q.insert_one(qe)
    
    qe = {"status":1,
          "lastSeen": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
           "uri1":"http://vocab.getty.edu/ulan/500020062",
           "uri2":"http://edan.si.edu/saam/id/person-institution/26558",
           "decision": [] #Should be updated in submit answer
         }
    q.insert_one(qe)
    
# Populate default set of questions from csv file
def populateQuestionsFromCSV(dbC,dname,csvfname):
    q = dbC[dname]["question"]
    
    with open(csvfname, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            if len(row) == 2:
                qe = {"status":1,
                      "lastSeen": datetime.datetime.utcnow(),
                      "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                              dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
                       "uri1":row[0],
                       "uri2":row[1],
                       "decision": [] #Should be updated in submit answer
                     }
                q.insert_one(qe)
        
# Retrieve set of questions from database based on tags, lastseen, unanswered vs in progress
def getQuestion(dbC,dname,uid):
    #user = dbC[dname]["curator"].find_one({'uid':uid})
    #question = dbC[dname]["question"].find_one({'tags':user.tags})
    #q = dbC[dname]["question"].find({"status":default_status})
    #print q
    #return random.choice(q)
    q = dbC[dname]["question"].find_one({"status":1})
    return q

#Answer
    #value, Integer value - 1 - Yes, 2 - No, 3 - Not Sure
    #comment, String optional 
    #author, String - uid of curator 
def submitAnswer(dbC, dname, qid, answer):
    # Add answer to database
    a = dbC[dname]["answer"]
    aid = a.insert_one(answer).inserted_id
    
    # from qid retrieve question 
    q = dbC[dname]["question"].find_one({'_id':qid})
    
    if q != None:
        # update descision with answer object id
        q['decision'] = q['decision']+[aid]
        # retrieve all answers
        ans = []
        noYes = 0
        noNo = 0
        noNotSure = 0
        for aid in q['decision']:
            a = dbC[dname]["answer"].find_one({'_id':aid})
            ans = ans+[a]        
            if ans['value'] == 1:
                noYes = noYes + 1
            elif ans['answer'] == 2:
                noNo = noNo + 1
            elif ans['value'] == 3:
                noNotSure = noNotSure + 1
                
        # Update status of the question based on different answers
        if noYes !=0 and noNo != 0:
            if noYes - noNo > confedenceLevel:
                if noNo >= contrastLevel:
                    q['status'] = 3 # Update to in Disagreement 
                else:
                    q['status'] = 4 # Update to in Completed 
            else:
                q['status'] = 2 # Update to in Progress 
    
        print q # Print new values of question before updating database
        #update database entry of question with new status and decision
        dbC[dname]["question"].find_one_and_update({'_id': qid},{'$set': {'status':q['status'],'decision':q['decision']}}) 