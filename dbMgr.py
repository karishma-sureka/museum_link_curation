import datetime
from random import randint
import csv
import json
import os
from pprint import pprint
from pymongo import MongoClient, ReturnDocument, ASCENDING, DESCENDING
from bson.objectid import ObjectId

confedenceLevel = 2
contrastLevel = 2

# Print the database just to check current data
def printDatabases(dbC,dname):
    print "\nPrinting ",dname," if it exists"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "\nPrinting Collection ",cname
        for val in dbC[dname][cname].find():
            print " \n", val
        print "\n"

# Removes all the data from all tables of given database
def cleanDatabases(dbC,dname):
    print "\nDropping database",dname,"if it exists\n"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "\nDropping collection (aka database)",cname,"\n"
        for val in dbC[dname][cname].find():
            print "\nDropping: ",val
        dbC[dname][cname].delete_many({})
        dbC[dname][cname].drop()
    print "\n"

# Clean particular Document from a Collection        
def printDatabase(dbC,dname,docname):
    print "\nPrinting Collection ",docname
    for val in dbC[dname][docname].find():
        print " \n", val
    print "\n"
    
# Clean particular Document from a Collection
def cleanDatabase(dbC,dname,docname):
    print "\nDropping collection (aka database)",docname,"\n"
    for val in dbC[dname][docname].find():
        print "\nDropping: ",val
    dbC[dname][docname].delete_many({})
    dbC[dname][docname].drop()            
    print "\n"
            
# Create database with default values for curation
def createDatabase(dbC,dname):
    populateTags(dbC,dname)
    #populateCurators(dbC,dname)
    
    ### Question (Pair of URIs) from different database
    #populateQuestions(dbC,dname)
    populateQuestionsFromCSV(dbC,dname, os.path.join('data', 'sample.csv'))
    #populateQuestionsFromJSON(dbC,dname, os.path.join('data','questions.json'))
    
    ### Entities from different database
    populateEntitiesFromJSON(dbC,dname, os.path.join('data', 'entities','sample.json'))
    #populateEntitiesFromJSON(dbC,dname, os.path.join('data', 'entities','DBPedia_architect.json'))
    #populateEntitiesFromJSON(dbC,dname, os.path.join('data', 'entities','DBPedia_artist.json'))
    #populateEntitiesFromJSON(dbC,dname, os.path.join('data', 'entities','NPG.json'))
    #populateEntitiesFromJSON(dbC,dname, os.path.join('data', 'entities','SAAM.json'))
    #populateEntitiesFromJSON(dbC,dname, os.path.join('data', 'entities','ULAN.json'))

#Artists
    #Schema as per Schema.org (Coverted by Yi Ding from different museum schema)
def populateEntitiesFromJSON(dbC,dname,filename):
    json_data=open(filename).read()
    data = json.loads(json_data)
    # Change this range on actual server
    for i in range(0,len(data["people"])):
    #for i in range(0,3):
        #pprint(data["people"][i])
        dbC[dname]["artists"].insert_one(data["people"][i])
        
#Tag
    #tagname, string 
# Populate database with default tags
def populateTags(dbC,dname):
    te = {"tagname":"autry"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"dbpedia"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"npg"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"saam"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"ulan"}
    dbC[dname]["tag"].insert_one(te)
    te = {"tagname":"viaf"}
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
          "tags":[dbC[dname]["tag"].find_one({'tagname':"ulan"})['_id'],
                  dbC[dname]["tag"].find_one({'tagname':"saam"})['_id'] ],
          "rating":5}
    dbC[dname]["curator"].insert_one(ce)
    ce = {"uid":"ksureka@usc.edu",
          "name":"Karishma Sureka",
          "tags":[dbC[dname]["tag"].find_one({'tagname':"ulan"})['_id'],
                  dbC[dname]["tag"].find_one({'tagname':"saam"})['_id'] ],
          "rating":5}
    dbC[dname]["curator"].insert_one(ce)

# Add the new curator from the client interface
def addCurator(dbC, dname, ce):
    dbC[dname]["curator"].insert_one(ce)
    printDatabase(dbC,dname,"curator")
    
# Question
    #status, integer: 1 - Not Started, 2 - In Progress, 3 - Completed, 4 - Disagreement
    #uniqueURI, String: alphabatical concatination of two URI to get unique ID
    #lastSeen, datetime field to select question based on time it was asked to previous curator
    #tags, list of object IDs from Tags
    #uri1, for now, just a URI related to a specific artist
    #uri2, for now, just another URI related to same specific artist
    #decision, list of object IDs from Answer
    #dedupe , dict, data coming from dedupe 
    
# Populate default set of questions
def populateQuestions(dbC,dname):    
    qe = {"status":1,
          "uniqueURI":generateUniqueURI("http://vocab.getty.edu/ulan/500028092","http://edan.si.edu/saam/id/person-institution/1681"),
          "lastSeen": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"ulan"})['_id'],
                  dbC[dname]["tag"].find_one({'tagname':"saam"})['_id'] ],
           "uri1":"http://vocab.getty.edu/ulan/500028092",
           "uri2":"http://edan.si.edu/saam/id/person-institution/1681",
           "decision": [], #Should be updated in submit answer
           "dedupe ": {}
         }
    dbC[dname]["question"].insert_one(qe)
    
    qe = {"status":1,
          "uniqueURI":generateUniqueURI("http://vocab.getty.edu/ulan/500020062","http://edan.si.edu/saam/id/person-institution/26558"),
          "lastSeen": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"ulan"})['_id'],
                  dbC[dname]["tag"].find_one({'tagname':"saam"})['_id'] ],
           "uri1":"http://vocab.getty.edu/ulan/500020062",
           "uri2":"http://edan.si.edu/saam/id/person-institution/26558",
           "decision": [], #Should be updated in submit answer
           "dedupe ": {}
         }
    dbC[dname]["question"].insert_one(qe)

def populateQuestionsFromJSON(dbC,dname,filename):
    json_data=open(filename).read()
    data = json.loads(json_data)
    count = data["bulk"]
    data = data["payload"]
    # Change this range on actual server
    for i in range(0,count):
    #for i in range(0,20):
        pprint(data[i])
        qe = {"status":1,
          "uniqueURI":generateUniqueURI(data[i]["uri1"],data[i]["uri2"]),
          "lastSeen": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':findTag(data[i]["uri1"])})['_id'],
                  dbC[dname]["tag"].find_one({'tagname':findTag(data[i]["uri2"])})['_id'] ],
           "uri1":data[i]["uri1"],
           "uri2":data[i]["uri2"],
           "decision": [], #Should be updated in submit answer
           "dedupe ": data[i]["dedupe"]
         }
        dbC[dname]["question"].insert_one(qe)
        
#Find tag from the URL
def findTag(uri):
    tag = "Default Tag"
    if "/dbpedia.org/" in uri:
        tag = "dbpedia"
    elif "/npgConstituents/" in uri:
        tag = "npg"
    elif "/saam/" in uri:
        tag = "saam"
    elif "/ulan/" in uri:
        tag = "ulan"
    return tag
    
def getTags(dbC,dname,entity):
    tags = []
    for tag in entity["tags"]:
        tags = tags + [dbC[dname]["tag"].find_one({'_id':ObjectId(tag)})["tagname"]]
    return tags
 
def checkURIOrdering(uri1,uri2):
    # Keep adding new database here. 
    # Internal ordering does not matter as we are just interested in single ordering between any pair of two database
    ordering = {"/dbpedia.org/":1,"/npgConstituents/":2,"/saam/":3,"/ulan/":4}
    
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
        return False
    else:
        return True

def generateUniqueURI(uri1,uri2):
    if checkURIOrdering(uri1,uri2):
        return uri1+uri2
    else:
        return uri2+uri1
 
# Populate default set of questions from csv file
def populateQuestionsFromCSV(dbC,dname,csvfname):
    with open(csvfname, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            if len(row) == 2:
                qe = {"status":1,
                      "uniqueURI":generateUniqueURI(row[0],row[1]),
                      "lastSeen": datetime.datetime.utcnow(),
                      "tags":[dbC[dname]["tag"].find_one({'tagname':findTag(row[0])})['_id'],
                              dbC[dname]["tag"].find_one({'tagname':findTag(row[1])})['_id'] ],
                       "uri1":row[0],
                       "uri2":row[1],
                       "decision": [], #Should be updated in submit answer
                       "dedupe ": {}
                     }
                dbC[dname]["question"].insert_one(qe)
        
def addOrUpdateQuestion(dbC,dname,uri1,uri2,dedupe):
    uuri = generateUniqueURI(uri1,uri2)
    q = dbC[dname]["question"].find_one({'uniqueURI':uuri})
    
    # If uuri exists, ignore dedupe as this request is coming second time, just return decision
    if q != None:
        print "Question instance already exists\n"
        return q["decision"]
    # Create new question and add dedupe information as well
    else:
        qe = {"status":1,
              "uniqueURI":uuri,
              "lastSeen": datetime.datetime.utcnow(),
              "tags":[dbC[dname]["tag"].find_one({'tagname':findTag(uri1)})['_id'],
                      dbC[dname]["tag"].find_one({'tagname':findTag(uri2)})['_id'] ],
               "uri1":uri1,
               "uri2":uri2,
               "decision": [], #Should be updated in submit answer
               "dedupe ": dedupe 
             }
        dbC[dname]["question"].insert_one(qe)
        return None
        
# Retrieve set of questions from database based on tags, lastseen, unanswered vs in progress
def getQuestionsForUID(dbC,dname,uid,count):
    # Filter-1: Find tags associated with uid and retrieve set of questions
    # Filter-2: Sort questions list based on status as InProgress or not started
    # Filter-3: Sort questions list whose status is NotStarted on maximum lastSeen 
    q1 = dbC[dname]["question"].find({"status":1}).sort([("lastSeen", DESCENDING)])
    q2 = dbC[dname]["question"].find({"status":2}).sort([("status", DESCENDING)])
    q = []
    
    # Filter-4: Remove questions that are already served to this user based on uid as author in decision
    userOid = dbC[dname]["curator"].find_one({'uid':uid})['_id']
    if userOid == None:
        print "User not found"
        return None
    
    #print "Found uid's objectID ",userOid
    
    # Check every question whose status is in progress
    for question in q2:
        aids = question["decision"]
        
        answered = False
        
        # Check authors in all answers if current user has already answered the question
        for aid in aids:
            if dbC[dname]["answer"].find_one({'_id':ObjectId(aid)})["author"] == ObjectId(userOid):
                answered = True
                break
        
        # If question is not answered previously add it to set of question to be sent.
        if answered != True:
            q = q + [question]
    
    for question in q1:
        q = q + [question]
        
    #return = dbC[dname]["question"].find({"status":1},skip=randint(0,dbC[dname]["question"].count()-1),limit=count)
    return q[:count]
        
def getMatches(left,right):
    exactMatch = {"name":[],"value":[]}
    unmatched = {"name":["URI"],"lValue":[left["@id"]],"rValue":[right["@id"]]}
    
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

def getStats(dbC,dname,q):
    noNo = 0
    noYes = 0
    noNotSure = 0
    for aid in q['decision']:
        a = dbC[dname]["answer"].find_one({'_id':ObjectId(aid)})
        if a != None:
            if a["value"] == "1":
                noYes = noYes + 1
            elif a["value"] == "2":
                noNo = noNo + 1
            elif a["value"] == "3":
                noNotSure = noNotSure + 1
                
    return {"Yes":noYes,"No":noNo,"Not Sure":noNotSure}
    
#Answer
    #value, Integer value - 1 - Yes, 2 - No, 3 - Not Sure
    #comment, String optional 
    #author, String - uid of curator 
def submitAnswer(dbC, dname, qid, answer, uid):
    
    # from qid retrieve question 
    q = dbC[dname]["question"].find_one({'_id':ObjectId(qid)})
    
    if q == None:
        #print "Submit answer failed for qid: ", qid
        message = "Question not found for qid: ",qid
        return {"status":False,"message":message}
    elif q['status'] == 3 or q['status'] == 4:
        #print "Question has already been answered by prescribed number of curators, qid: ", qid
        message = "Predetermined number of curators have already answered question with qid: ", qid
        return {"status":False,"message":message}
    else:
        #print "Found the question"
        
        #Check if user has already answered the question
        # Check authors in all answers if current user has already answered the question
        for aid in q["decision"]:
            if dbC[dname]["answer"].find_one({'_id':ObjectId(aid)})["author"] == uid:
                #print "User has already submitted answer to question ", qid
                message = "User has already submitted answer to question witg qid ", qid
                return {"status":False,"message":message}
        
        # Add answer to database
        a = dbC[dname]["answer"]
        aid = a.insert_one(answer).inserted_id
        #print "Inserted new answer with aid: ", aid
        #print "answers ",a
    
        # update decision with answer object id
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
            #projection={'_id':False,'status':True},
            return_document=ReturnDocument.AFTER)
        
        
        print "\n Updated question document \n",q
        #printDatabase(dbC,dname,"answer")
        return {"status":True,"message":"Appended answer to question's decision list"}
