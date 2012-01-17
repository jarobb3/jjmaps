import webapp2
import os
import models
import helpers
import json
#import pprint

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Maps(webapp2.RequestHandler):
    def get(self):
        chapters = models.getallchapters()
        
        if self.request.get('chapterkey'):
            chapterkey = self.request.get('chapterkey')
            chapter = models.getchapter(chapterkey)
            c = self.coordsfromchapterkey(chapter)
                    
            template_values = { 'chapters' : chapters, 'chapter' : chapter, 'coords' : json.dumps(c) }
        else: 
            template_values = { 'chapters' : chapters, 'coords' : [], 'chaptername' : [] }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/map.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        chapterkey = self.request.get('chapterkey')
        chapter = models.getchapter(chapterkey)
        c = self.coordsfromchapterkey(chapter)
        
        self.response.out.write( json.dumps({ 'chaptername' : chapter.name, 'chapterkey' : chapterkey, 'coords' : c }) )
        
    def coordsfromchapterkey(self,chapter):
        zipinds = chapter.zipinds
        countyinds = chapter.countyinds
        state = chapter.state
        
        zipsfilearr = map(helpers.mapkill,helpers.getdatafilearray('data/' + state + '/zip/complex.txt'))
        countysfilearr = map(helpers.mapkill,helpers.getdatafilearray('data/' + state + '/county/complex.txt'))
                
        c = []
        for zi in zipinds:
            coords = helpers.getcoordsfromindex(zipsfilearr,zi)
            if coords:
                c.append(map(' '.join,coords))
                
        for ci in countyinds:
            coords = helpers.getcoordsfromindex(countysfilearr, ci)
            if coords:
                c.append(map(' '.join,coords))
        return c
        
class Chapters(webapp2.RequestHandler):
    def get(self):
        chapters = models.getallchapters()
        
        if self.request.get('chapterkey'):
            chapterkey = self.request.get('chapterkey')
            chapter = models.getchapter(chapterkey)
            template_values = { 'chapter' : chapter, 'chapters' : chapters }
        else:
            template_values = { 'chapters' : chapters }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/chapters.html')
        self.response.out.write(template.render(path, template_values))
        
class ChaptersUpdate(webapp2.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        #query database to see if this entry already exists (query by chaptername and state)
        if self.request.get('chapterkey'):
            chapter = models.getchapter(self.request.get('chapterkey'))
        else:
            chapter = models.Chapter()
        
        zips = self.request.get('chapterzips')
        counties = self.request.get('chaptercounties')
        
        chapter.name = self.request.get('chaptername')
        chapter.state = self.request.get('chapterstate').upper()
        
        if zips: chapter.zips = map(helpers.mapstrip, zips.split(","))
        else: chapter.zips = ['Null']
        
        if counties: chapter.counties = map(helpers.mapstrip, counties.split(","))
        else: chapter.counties = ['Null']
            
        if chapter.counties[0] != 'Null':
            countydataarr = map(helpers.quotekill,helpers.getdatafilearray('data/' + chapter.state + '/county/simple.txt'))
            inds = helpers.findcountyindicies(countydataarr, chapter.counties)
            if not isinstance(inds,list):
                self.response.out.write(self.errorstr(inds))
                return
            chapter.countyinds = inds
        else:
            chapter.countyinds = []
        
        if chapter.zips[0] != 'Null':
            zipsdataarr = map(helpers.quotekill,helpers.getdatafilearray('data/' + chapter.state + '/zip/simple.txt'))
            zinds = helpers.findzipindicies(zipsdataarr, chapter.zips)
            if not isinstance(zinds,list):
                self.response.out.write(self.errorstr(zinds))
                return
            chapter.zipinds = zinds
        else:
            chapter.zipinds = []
         
        #print chapter.to_xml()   
        chapter.put()
        
        self.redirect('/chapters')
        
    def errorstr(self,errorobj):
        return """
            Update Error: %s -- %s. Please hit the Back button in your browser, check your spelling, and try again.
        """ % (errorobj['error'],"\""+errorobj['baditem']+"\"")
        
class ChaptersDelete(webapp2.RequestHandler):
    def get(self):
        chapterkey = self.request.get('chapterkey')
        
        models.deletechapterentry(chapterkey)
        self.redirect('/chapters')

class ChaptersClear(webapp2.RequestHandler):
    def get(self):
        models.deleteallchapters()
        self.redirect('/chapters')
        
class ChaptersCreateAuto(webapp2.RequestHandler):
    def get(self):
        state = self.request.get('state')
        
        chaptersdatafile = map(helpers.commakill,helpers.getdatafilearray('data/' + state.upper() + '/chapters.txt'))
        chaptersjson = helpers.chapterstojson(chaptersdatafile)
        
        for chaptername in chaptersjson:
            chapterjson = chaptersjson[chaptername]
            
            chapter = models.Chapter()
            chapter.name = chaptername
            chapter.state = state.upper()
            
            #countyfilepath = 'data/' + state + '/county/simple.txt'
            chapter.counties = chapterjson[0]
            if chapter.counties[0] != 'Null':
                countydataarr = map(helpers.quotekill,helpers.getdatafilearray('data/' + state + '/county/simple.txt'))
                chapter.countyinds = helpers.findcountyindicies(countydataarr, chapter.counties)
            else:
                chapter.countyinds = []
            
            #zipsfilepath = 'data/' + state + '/zip/simple.txt'
            chapter.zips = chapterjson[1]
            if chapter.zips[0] != 'Null':
                zipsdataarr = map(helpers.quotekill,helpers.getdatafilearray('data/' + state + '/zip/simple.txt'))
                chapter.zipinds = helpers.findzipindicies(zipsdataarr, chapter.zips)
            else:
                chapter.zipinds = []
  
            chapter.put()
            
        self.redirect('/chapters')
        
class test(webapp2.RequestHandler):
    def get(self):
        chapters = models.getallchapters()

        template_values = { 'chapters' : chapters }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/test.html')
        self.response.out.write(template.render(path, template_values))
        
app = webapp2.WSGIApplication([
                               ('/', Maps),
                               ('/map', Maps),
                               ('/chapters', Chapters),
                               ('/chapters/update',ChaptersUpdate),
                               ('/test', test),
                               ('/chapters/create/auto', ChaptersCreateAuto),
                               ('/chapters/clear', ChaptersClear),
                               ('/chapters/delete', ChaptersDelete)]
                              ,debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == "__main__":
    main()