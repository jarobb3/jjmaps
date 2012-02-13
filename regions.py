import webapp2
import models
import helpers
import json

from google.appengine.ext.webapp.util import run_wsgi_app

class RegionsUpdate(webapp2.RequestHandler):
    def post(self):
        regionname = self.request.get('regionname')
        region = models.Region()
        
        region.name = regionname
        region.put()
        
        self.redirect('/chapters')
        
'''
RegionsAddState: Adds a state to a region
'''
class RegionsAddState(webapp2.RequestHandler):   
    def post(self):
        regionkey = self.request.get('regionkey')
        statecode = self.request.get('statecode')
        regionname = self.request.get('regionname')
        
        chapters = models.getchaptersinstate(statecode)
        for chapter in chapters:
            newchapter = models.Chapter(parent=models.keyfromstr(regionkey))
            newchapter.name = chapter.name
            newchapter.state = chapter.state
            newchapter.zips = chapter.zips
            newchapter.zipinds = chapter.zipinds
            newchapter.counties = chapter.counties
            newchapter.countyinds = chapter.countyinds
            
            newchapter.put()
            models.deletechapterentry(chapter.key())
        
        self.response.out.write( json.dumps({ 'regionkey' : regionkey, 'regionname' : regionname }) )
        
'''
RegionsRemoveState: Removes a state from a region
'''
class RegionsRemoveState(webapp2.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        #regionkey = self.request.get('regionkey')
        statecode = self.request.get('statecode')
        
        chapters = models.getchaptersinstate(statecode)
        for chapter in chapters:
            newchapter = models.Chapter()
            newchapter.name = chapter.name
            newchapter.state = chapter.state
            newchapter.zips = chapter.zips
            newchapter.zipinds = chapter.zipinds
            newchapter.counties = chapter.counties
            newchapter.countyinds = chapter.countyinds
            
            newchapter.put()
            models.deletechapterentry(chapter.key())
            
        self.response.out.write( json.dumps({ }) )
            
class RegionsGetChapters(webapp2.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        regionkey = self.request.get('regionkey')
        chapters = models.getchaptersinregion(models.keyfromstr(regionkey))
        
        chapterkeys = []
        for ch in chapters:
            chapterkeys.append(str(ch.key()))
             
        self.response.out.write( json.dumps({ 'chapterkeys' : chapterkeys }) )

    
class RegionsShowOnMap(webapp2.RequestHandler):
    def post(self):
        regionkey = self.request.get('regionkey')
        region = models.getregion(regionkey)
        chapters = models.getchaptersinregion(region)
       
        chaptersdict = []
        for c in chapters:
            coords = helpers.coordsfromchapterkey(c)
            chapterkey = c.key()
            
            chapterdict = models.to_dict(c)
            chapterdict['coords'] = coords
            chapterdict['key'] = str(chapterkey)
            
            chaptersdict.append(chapterdict)         
            
        self.response.out.write( json.dumps({ 'chapters' : chaptersdict, 'regionkey' : regionkey }) )      

app = webapp2.WSGIApplication([
                               ('/regions/show', RegionsShowOnMap),
                               ('/regions/create', RegionsUpdate),
                               ('/regions/add-state', RegionsAddState),
                               ('/regions/remove-state', RegionsRemoveState),
                               ('/regions/get-chapters', RegionsGetChapters)]
                              ,debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == "__main__":
    main()