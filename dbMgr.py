import datetime
from random import randint
import csv
import json
import os
from pprint import pprint
from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId

confedenceLevel = 2
contrastLevel = 2

# Print the database just to check current data
def printDatabases(dbC,dname):
    print "\n Printing ",dname," if it exists"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "\n Printing Collection ",cname
        for val in dbC[dname][cname].find():
            print " \n", val

# Removes all the data from all tables of given database
def cleanDatabases(dbC,dname):
    print "\n Dropping database",dname,"if it exists\n"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "\n Dropping collection (aka database)",cname,"\n"
        for val in dbC[dname][cname].find():
            print "\nDropping: ",val
        dbC[dname][cname].delete_many({})
        dbC[dname][cname].drop()

# Clean particular Document from a Collection        
def printDatabase(dbC,dname,docname):
    print "\n Printing Collection ",docname
    for val in dbC[dname][docname].find():
        print " \n", val
            
# Clean particular Document from a Collection
def cleanDatabase(dbC,dname,docname):
    print "\n Dropping collection (aka database)",docname,"\n"
    for val in dbC[dname][docname].find():
        print "\nDropping: ",val
    dbC[dname][docname].delete_many({})
    dbC[dname][docname].drop()            
            
# Create database with default values for curation
def createDatabase(dbC,dname):
    populateTags(dbC,dname)
    populateCurators(dbC,dname)
    #populateQuestions(dbC,dname)
    populateQuestionsFromCSV(dbC,dname, os.path.join('data', 'sample.csv'))
    
    # Not required to be populated
    # Save on the fly as per the PUT request 
    #saveAnswers(dbC,dname) 
    
    loadDataFromJson(dbC,dname, os.path.join('data', 'sample.json'))

#Artists
    #Schema as per Schema.org (Coverted by Yi Ding from different museum schema)
def loadDataFromJson(dbC,dname,filename):
    json_data=open(filename).read()
    data = json.loads(json_data)
    for i in range(0,2):
        #pprint(data["people"][i])
        dbC[dname]["artists"].insert_one(data["people"][i])
    
#Tag
    #tagname, string 
# Populate database with default tags
def populateTags(dbC,dname):
    te = {"tagname":"randomtag1"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"randomtag2"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"randomtag3"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"randomtag4"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"randomtag5"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"randomtag6"}
    dbC[dname]["tag"].insert_one(te)
    
#Curator
    #uid, String - userID
    #name, String
    #rating, Integer
    #questionsSeen, List of object IDs from Question
    #tags, list of object IDs from Tags
    
# Populate database with default curators
def populateCurators(dbC,dname):
    ce = {"uid":"nilayvac@usc.edu",
          "name":"Nilay Chheda",
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag1"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag4"})],
          "rating":5}
    dbC[dname]["curator"].insert_one(ce)
    ce = {"uid":"ksureka@usc.edu",
          "name":"Karishma Sureka",
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
          "rating":5}
    dbC[dname]["curator"].insert_one(ce)

# Add the new curator from the client interface
def addCurator(dbC, dname, ce):
    dbC[dname]["curator"].insert_one(ce)
    
# Question
    #status, integer: 1 - Not Started, 2 - In Progress, 3 - Completed, 4 - Disagreement
    #uniqueURI, String: alphabatical concatination of two URI to get unique ID
    #lastSeen, datetime field to select question based on time it was asked to previous curator
    #tags, list of object IDs from Tags
    #uri1, for now, just a URI related to a specific artist
    #uri2, for now, just another URI related to same specific artist
    #decision, list of object IDs from Answer
    #dedup, dict, data coming from dedup
    
# Populate default set of questions
def populateQuestions(dbC,dname):    
    qe = {"status":1,
          "uniqueURI":generateUniqueURI("http://vocab.getty.edu/ulan/500028092","http://edan.si.edu/saam/id/person-institution/1681"),
          "lastSeen": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag1"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag4"})],
           "uri1":"http://vocab.getty.edu/ulan/500028092",
           "uri2":"http://edan.si.edu/saam/id/person-institution/1681",
           "decision": [], #Should be updated in submit answer
           "dedup": {}
         }
    dbC[dname]["question"].insert_one(qe)
    
    qe = {"status":1,
          "uniqueURI":generateUniqueURI("http://vocab.getty.edu/ulan/500020062","http://edan.si.edu/saam/id/person-institution/26558"),
          "lastSeen": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
           "uri1":"http://vocab.getty.edu/ulan/500020062",
           "uri2":"http://edan.si.edu/saam/id/person-institution/26558",
           "decision": [], #Should be updated in submit answer
           "dedup": {}
         }
    dbC[dname]["question"].insert_one(qe)
    
# Populate default set of questions from csv file
def populateQuestionsFromCSV(dbC,dname,csvfname):
    with open(csvfname, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            if len(row) == 2:
                qe = {"status":1,
                      "uniqueURI":generateUniqueURI(row[0],row[1]),
                      "lastSeen": datetime.datetime.utcnow(),
                      "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                              dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
                       "uri1":row[0],
                       "uri2":row[1],
                       "decision": [], #Should be updated in submit answer
                       "dedup": {}
                     }
                dbC[dname]["question"].insert_one(qe)
        
def addOrUpdateQuestion(dbC,dname,uri1,uri2,dedup):
    uuri = generateUniqueURI(uri1,uri2)
    q = dbC[dname]["question"].find_one({'uniqueURI':uuri})
    
    # If uuri exists, ignore dedup as this request is coming second time, just return decision
    if q != None:
        return q["decision"]
    # Create new question and add dedup information as well
    else:
        qe = {"status":1,
              "uniqueURI":uuri,
              "lastSeen": datetime.datetime.utcnow(),
              "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                      dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
               "uri1":uri1,
               "uri2":uri2,
               "decision": [], #Should be updated in submit answer
               "dedup": dedup
             }
        dbC[dname]["question"].insert_one(qe)
        return None

def generateUniqueURI(uri1,uri2):
    # Keep adding new database here. 
    # Internal ordering does not matter as we are just interested in single ordering between any pair of two database
    ordering = {"http://edan.si.edu/saam":1,"http://vocab.getty.edu/ulan":2}
    val1 = 0
    val2 = 0
    for key in ordering.keys():
        if key in uri1:
            val1 = ordering[key]
            break;
    
    for key in ordering.keys():
        if key in uri2:
            val2 = ordering[key]
            break;
    
    if val1 > val2:
        return uri2+uri1
    else:
        return uri1+uri2
        
# Retrieve set of questions from database based on tags, lastseen, unanswered vs in progress
def getQuestionsForUID(dbC,dname,uid):
    # Filter-1: Find tags associated with uid and retrieve set of questions
    # Filter-2: Sort questions list based on status as InProgress
    # Filter-3: Sort questions list whose status is NotStarted on maximum lastSeen 
    # Filter-4: Remove questions that are already served to this user based on uid as author in decision
    
    q = dbC[dname]["question"].find({"status":1},skip=randint(0,dbC[dname]["question"].count()-1),limit=5)
    return q
        
def getMatches(left,right):
    
    if left == None or right == None:
        return {"ExactMatch":None,"Unmatched":None}
    
    exactMatch = {"name":[],"value":[]}
    #exactMatch = {}
    unmatched = {"name":[],"lValue":[],"rValue":[]}
    #unmatched = {}
    
    fields = ["schema:name","schema:additionalName","schema:nationality","schema:birthDate","schema:deathDate","schema:birthPlace"]
    
    for field in fields:
        if field in left and field in right:
            if left[field] == right[field]:
                exactMatch["name"] = exactMatch["name"]+[field]
                exactMatch["value"] = exactMatch["value"]+[left[field]]
            else:
                unmatched["name"] = unmatched["name"]+[field]
                unmatched["lValue"] = unmatched["lValue"]+[left[field]]
                unmatched["rValue"] = unmatched["rValue"]+[right[field]]
        elif field in left:
            unmatched["name"] = unmatched["name"]+[field]
            unmatched["lValue"] = unmatched["lValue"]+[left[field]]
            unmatched["rValue"] = unmatched["rValue"]+[None]
        elif field in right:
            unmatched["name"] = unmatched["name"]+[field]
            unmatched["lValue"] = unmatched["lValue"]+[None]
            unmatched["rValue"] = unmatched["rValue"]+[right[field]]
    return {"ExactMatch":exactMatch,"Unmatched":unmatched}
    
#Answer
    #value, Integer value - 1 - Yes, 2 - No, 3 - Not Sure
    #comment, String optional 
    #author, String - uid of curator 
def submitAnswer(dbC, dname, qid, answer):
    # Add answer to database
    a = dbC[dname]["answer"]
    aid = a.insert_one(answer).inserted_id
    #print "Inserted new answer with aid: ", aid
    #print "answers ",a
    
    # from qid retrieve question 
    q = dbC[dname]["question"].find_one({'_id':ObjectId(qid)})
    
    if q == None:
        print "Submit answer failed for qid: ", qid
        return False
    else:
        #print "Found the question"
        # update descision with answer object id
        q['decision'] = q['decision']+[aid]
        #print "decision is: ", q['decision']
        
        # retrieve all answers
        noYes = 0
        noNo = 0
        noNotSure = 0
        
        #printDatabase(dbC,dname,"answer")
        
        for aid in q['decision']:
            a = dbC[dname]["answer"].find_one({'_id':ObjectId(aid)})
            if a != None:
                if a["value"] == "1":
                    noYes = noYes + 1
                elif a["value"] == "2":
                    noNo = noNo + 1
                elif a["value"] == "3":
                    noNotSure = noNotSure + 1
                 
        #print "current Y/N/NA: ",noYes,noNo,noNotSure
        
        # Update status of the question based on different answers
        if noYes !=0 or noNo != 0:
            if noYes - noNo >= confedenceLevel:
                if noNo >= contrastLevel:
                    q['status'] = 3 # Update to, Disagreement 
                else:
                    q['status'] = 4 # Update to, Completed 
            else:
                if noNo >= contrastLevel:
                    q['status'] = 3 # Update to, Disagreement 
                else:
                    q['status'] = 2 # Update to, InProgress
    
        #update database entry of question with new status and decision
        q =  dbC[dname]["question"].find_one_and_update(
            {'_id':ObjectId(qid)},
            {'$set': {'status':q['status'],'decision':q['decision']}},
            #projection={'_id':False,'status':True,},
            return_document=ReturnDocument.AFTER)
        print "\n Updated question document \n",q
        return True