from google.appengine.ext import db

def keyfromstr(keystr):
    return db.Key(encoded=keystr)

class Region(db.Model):
    name = db.StringProperty()
    
def getallregions():
    return Region.all()

def getregion(key):
    return db.get(keyfromstr(key))

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
    
def getchaptersfromzip(zipcode):
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
    chapter = query.get()
    if chapter:
        return chapter.parent()
    return None

import datetime
import time

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def to_dict(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(value.utctimetuple()) * 1000
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))

    return output
    
def chapterstodict(chapters):
    clist = []
    for c in chapters:
        clist.append(to_dict(c))
         
    return clist