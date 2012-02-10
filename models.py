from google.appengine.ext import db

def keyfromstr(keystr):
    return db.Key(encoded=keystr)

class Region(db.Model):
    name = db.StringProperty()
    
def getallregions():
    return Region.all()

def getregion(key):
    return db.get(key)

def getchaptersinregion(regionkey):
    query = db.Query(Chapter)
    query.ancestor(regionkey)
    
    return query.run()

def numchaptersinregion(regionkey):
    query = db.Query(Chapter)
    query.ancestor(regionkey)
    
    return query.count()
    
class Chapter(db.Model):
    name = db.StringProperty()
    state = db.StringProperty()
    zips = db.ListProperty(str)
    zipinds = db.ListProperty(str)
    counties = db.ListProperty(str)
    countyinds = db.ListProperty(str)

def getchapter(key):
    return db.get(key)
    
def getallchapters():
    return Chapter.all()

def deleteallchapters():
    chapters = getallchapters()
    
    for chapter in chapters:
        chapter.delete() 
        
def deletechapterentry(key):
    chapter = getchapter(key)
    chapter.delete()
    
def getchapterfromzip(zipcode):
    query = db.Query(Chapter)
    query.filter('zips = ', zipcode)
    return query.run()

def getchaptersinstate(statecode):
    query = db.Query(Chapter)
    query.filter('state = ', statecode)
    return query.run()
    
    
def getregionfromstate(statecode):
    query = db.Query(Chapter)
    query.filter('state = ', statecode)
    chapterinstate = query.get()
    return chapterinstate.parent()
    