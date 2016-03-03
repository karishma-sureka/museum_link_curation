import datetime
#from flask import url_for
from app import db 

class Artist(db.Document):
    person = db.StringField(max_length=255)
    reference = db.StringField(max_length=255)
    #person = db.ReferenceField('Person',requied=True)
    #references = db.ListField(db.ReferenceField('Reference'))
    
class Status(db.EmbeddedDocument):
    # 1 - Not Started, 2 - In Progress, 3 - Completed, 4 - Disagreement
    value = db.IntField(max_length=4,required=True)
    description = db.StringField(max_length=255, required=True)

class Tag(db.Document):
    tagname = db.StringField(max_lenth=255,required=True)

class Curator(db.Document):
    uid = db.StringField(max_length=255,required=True) # Unique uid (primary key)
    name = db.StringField(max_length=255)
    rating = db.IntField(required = True)
    questionsSeen = db.ListField(db.ReferenceField('Question'))
    tags = db.ListField(db.ReferenceField('Tag'))
    
class Answer(db.Document):
    # 1 - Yes, 2 - No, 3 - Not Sure
    value = db.IntField(max_lenght=3,required=True)
    comment = db.StringField(max_length=255)
    author = db.ReferenceField('Curator')
    
class Question(db.Document):
    qid = db.IntField(required=True)    # Unique qid (primary key)
    status = db.EmbeddedDocumentField('Status', required=True)
    timestamp = db.DateTimeField(default=datetime.datetime.now, required=True)
    tags = db.ListField(db.ReferenceField('Tag'))
    uri1 = db.ReferenceField('Artist',required=True) #Here Museum artist
    uri2 = db.ReferenceField('Artist',required=True) #Here Museum artist
    decision = db.ListField(db.ReferenceField('Answer'))