from models import *

def clearData():
    Artist.objects = []
    Status.objects = []
    Tag.objects = []
    Curator.objects = []
    Answer.objects = []
    Question.objects = []
    print "Data Cleared"
     
def populateData():
    # artists
    a = Artist(person="Edward Hopper", reference="http://edan.si.edu/saam/id/person-institution/2297")
    a.save()
    a = Artist(person="Edward Hopper II", reference="http://dbpedia.org/page/Edward_Hopper")
    a.save()
    
    # Status (Not requied in main Db as these are used as embedded field in Question)
    # s = Status(value=1,description="Not Started")
    # s.save()
    # s = Status(value=2,description="In Progress")
    # s.save()
    # s = Status(value=3,description="Completed")
    # s.save()
    # s = Status(value=4,description="Disagreement")
    # s.save()
    
    # Tags 
    t = Tag(tagname="randomtag1")
    t.save()
    t = Tag(tagname="randomtag2")
    t.save()
    t = Tag(tagname="randomtag3")
    t.save()
        
    #Curator (Name, Rating, Tag can be created before hand but questionsSeen seen would update dynamically)
    
    # Sample curator
    c = Curator(uid="nilayvac@usc.edu",name="Nilay Chheda",rating=5)
    #c.tags= Tag.objects(tagname__iexact='Randomtag3')
    c.save()
    
    # Sampe Question
    q = Question(qid=1,status=Status(value=1,description="Not Started"),timestamp=datetime.datetime.now)
    #q.tags= Tag.objects(tagname__iexact='Randomtag3')
    
    
    #uris = [Artist.objects(person__contains="Edward Hopper")]
    #if (len(uris) > 2):
        #q.uri1 = uris[0]
        #q.uri2 = uris[1]
    
    
    # uris = []
    # for uri in Artist.objects:
        # print "URI is : "+uri
        # uris = uris + [uri]
    
    # q.uri1 = uris[0]
    # q.uri2 = uris[1]
    
    #q.save()

def get_question(uid):
    # User uid to get relevant questions
    qs = None
    
    # for q in Question.objects:
        # qs = q
        # break
    
    qs = Question(qid=1,status=Status(value=1,description="Not Started"),timestamp=datetime.datetime.now)
    uri1 = Artist(person="Edward Hopper", reference="http://edan.si.edu/saam/id/person-institution/2297")
    uri1.save()
    uri2 = Artist(person="Edward Hopper II", reference="http://dbpedia.org/page/Edward_Hopper")
    uri2.save()
    qs.uri1 = uri1
    qs.uri2 = uri2
    
    return qs

def submit_answer(qid,ans):
    ans.author.save()
    ans.save()
    # Use qid to update question status
    #qid.
    return ans