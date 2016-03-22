import datetime
import random
from pymongo import MongoClient

def printDatabase(dbC,dname):
    print "Printing ",dname," if it exists"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "Collection ",cname
        for val in dbC[dname][cname].find():
            print " Document ", val

def createDatabase(dbC,dname):
    populateTags(dbC,dname)
    populateCurators(dbC,dname)
    populateQuestions(dbC,dname)
    
    # Not required to be populated
    # Save on the fly as per the PUT request 
    #saveAnswers(dbC,dname) 
    
    #populateRefURI(dbC,dname)
    
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
    
def populateCurators(dbC,dname):
    c = dbC[dname]["curator"]
    ce = {"uid":"nilayvac@usc.edu",
          "name":"Nilay Chheda",
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag1"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag4"})],
          "rating":5}
    c.insert_one(ce)

def populateQuestions(dbC,dname):
    q = dbC[dname]["question"]
    default_status = {"value":1,"desc":"Not Started"}
    
    qe = {"status":default_status,
          "timestamp": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag1"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag4"})],
           "uri1":"http://vocab.getty.edu/ulan/500028092",
           "uri2":"http://edan.si.edu/saam/id/person-institution/1681"
           #"decision": Should be updated in submtit answer
         }
    q.insert_one(qe)
    
    qe = {"status":default_status,
          "timestamp": datetime.datetime.utcnow(),
          "tags":[dbC[dname]["tag"].find_one({'tagname':"randomtag2"}),
                  dbC[dname]["tag"].find_one({'tagname':"randomtag3"})],
           "uri1":"http://vocab.getty.edu/ulan/500020062",
           "uri2":"http://edan.si.edu/saam/id/person-institution/26558"
           #"decision": Should be updated in submtit answer
         }
    q.insert_one(qe)
    
def cleanDatabase(dbC,dname):
    print "Dropping database",dname,"if it exists"
    for cname in dbC[dname].collection_names(include_system_collections=False):
        print "Dropping collection (aka database)",cname
        for val in dbC[dname][cname].find():
            print val
        dbC[dname][cname].delete_many({})
        dbC[dname][cname].drop()

def populateDatabase(dbC,dname):
    print "Creating database"

def getQuestion(dbC,dname,uid):
    #user = dbC[dname]["curator"].find_one({'uid':uid})
    #question = dbC[dname]["question"].find_one({'tags':user.tags})
    default_status = {"value":1,"desc":"Not Started"}
    q = dbC[dname]["question"].find_one({"status":default_status})
    return q
    
    #q = dbC[dname]["question"].find({"status":default_status})
    #print q
    #return random.choice(q)
    
# Sample Schema

# class Artist(db.Document):
    # person = db.StringField(max_length=255)
    # reference = db.StringField(max_length=255)
    # #person = db.ReferenceField('Person',requied=True)
    # #references = db.ListField(db.ReferenceField('Reference'))
    
# class Status(db.EmbeddedDocument):
    # # 1 - Not Started, 2 - In Progress, 3 - Completed, 4 - Disagreement
    # value = db.IntField(max_length=4,required=True)
    # desc = db.StringField(max_length=255, required=True)

# class Tag(db.Document):
    # tagname = db.StringField(max_lenth=255,required=True)

# class Curator(db.Document):
    # uid = db.StringField(max_length=255,required=True) # Unique uid (primary key)
    # name = db.StringField(max_length=255)
    # rating = db.IntField(required = True)
    # questionsSeen = db.ListField(db.ReferenceField('Question'))
    # tags = db.ListField(db.ReferenceField('Tag'))
    
# class Answer(db.Document):
    # # 1 - Yes, 2 - No, 3 - Not Sure
    # value = db.IntField(max_lenght=3,required=True)
    # comment = db.StringField(max_length=255)
    # author = db.ReferenceField('Curator')
    
# class Question(db.Document):
    # qid = db.IntField(required=True)    # Unique qid (primary key)
    # status = db.EmbeddedDocumentField('Status', required=True)
    # timestamp = db.DateTimeField(default=datetime.datetime.now, required=True)
    # tags = db.ListField(db.ReferenceField('Tag'))
    # uri1 = db.ReferenceField('Artist',required=True) #Here Museum artist
    # uri2 = db.ReferenceField('Artist',required=True) #Here Museum artist
    # decision = db.ListField(db.ReferenceField('Answer'))