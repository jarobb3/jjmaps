from google.appengine.ext import db
    
class Chapter(db.Model):
    name = db.StringProperty()
    state = db.ListProperty(str)
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
    