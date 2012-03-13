import webapp2
import os
import models
import helpers
import json

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Maps(webapp2.RequestHandler):
    def get(self):
        chapters = models.getallchapters()
        regions = models.getallregions()
        
        if self.request.get('chapterkey'):
            chapterkey = self.request.get('chapterkey')
            chapter = models.getchapter(chapterkey)
            c = self.coordsfromchapterkey(chapter)
                    
            template_values = { 'regions' : regions, 'chapters' : chapters, 'chapter' : chapter, 'coords' : json.dumps(c) }
        else: 
            template_values = { 'regions' : regions, 'chapters' : chapters, 'coords' : [], 'chaptername' : [] }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/map.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        if self.request.get('chapterkey'):
            chapters = [models.getchapter(self.request.get('chapterkey'))]
        elif self.request.get('regionkey'):
            chapters = models.getchaptersinregion(models.keyfromstr(self.request.get('regionkey'))) 
        else:
            pass
       
        chaptersdict = []
        for c in chapters:
            coords = helpers.coordsfromchapterkey(c)
            chapterkey = c.key()
            
            chapterdict = models.to_dict(c)
            chapterdict['coords'] = coords
            chapterdict['key'] = str(chapterkey)
            
            chaptersdict.append(chapterdict)         

        self.response.out.write( json.dumps({ 'chapters' : chaptersdict }) )
                
    def coordsfromchapterkey(self,chapter):
        domain = 'http://jandj.gldnfleece.com/'
        zipcoordsdata = {}
        countycoordsdata = {}
        
        c = []
        for county in chapter.countyinds:
            s = helpers.stateforcounty(county,chapter.state)
            countyind = county.split('|')[0]
            try:
                dataarr = countycoordsdata[s]
                coords = helpers.getcoordsfromindex(dataarr, countyind)
            except KeyError:
                countycoordsdata[s] = helpers.prepcoordsfile(domain + 'data/' + s + '/county/complex.txt')
                coords = helpers.getcoordsfromindex(countycoordsdata[s], countyind)
               
            if coords:
                c.append(map(' '.join,coords))
                
        for zipcode in chapter.zipinds:
            s = helpers.stateforzip(zipcode,chapter.state)
            zipind = zipcode.split('|')[0]
            try:
                dataarr = zipcoordsdata[s]
                coords = helpers.getcoordsfromindex(dataarr, zipind)
            except KeyError:
                zipcoordsdata[s] = helpers.prepcoordsfile(domain + 'data/' + s + '/zip/complex.txt')
                coords = helpers.getcoordsfromindex(zipcoordsdata[s], zipind)
            
            if coords:
                c.append(map(' '.join,coords))
        
        return c
    
class MapsSearch(webapp2.RequestHandler):
    def post(self):
        zipcodequery = self.request.get('q')
        chapters = models.getchaptersfromzip(zipcodequery)
            
        chaptersdict = []
        for c in chapters:
            coords = helpers.coordsfromchapterkey(c)
            chapterkey = c.key()
            
            chapterdict = models.to_dict(c)
            chapterdict['coords'] = coords
            chapterdict['key'] = str(chapterkey)
            
            chaptersdict.append(chapterdict)
        
        self.response.out.write( json.dumps({ 'chapters' : chaptersdict }) )
    
class MapsChangeTab(webapp2.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        tab = self.request.get('tabindex')
        
        if tab == 'chapters':
            chapters = models.getallchapters()
            response_values = { 'tab' : 'chapters', 'chapters' : chapters }
        else: #regions tab selected
            regions = models.getallregions()
            response_values = { 'tab' : 'regions', 'regions' : regions }
        
        self.response.out.write( json.dumps(response_values) )

app = webapp2.WSGIApplication([
                               ('/', Maps),
                               ('/map', Maps),
                               ('/map/search', MapsSearch),
                               ('/map/change-tab', MapsChangeTab)]
                              ,debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == "__main__":
    main()