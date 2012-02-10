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
        chapternames = []
        chapterkeys = []
        coords = []
        
        if self.request.get('chapterkey'):
            chapter = models.getchapter(self.request.get('chapterkey'))
            
            chapternames.append(chapter.name)
            #chapterkeys.append(self.request.get('chapterkey'))
            chapterkeys.append(str(chapter.key()))
            coords.append(self.coordsfromchapterkey(chapter))
    
        else:
            #lookup code path
            #need to be able to support showing multiple chapters in one request, which requires changes to this function and the AJAX JS
            #also need to support what happens if it's a county instead of a zip being looked up
            chapters = models.getchapterfromzip(self.request.get('q'))
            
            
            for ch in chapters:
                chapternames.append(ch.name)
                chapterkeys.append(str(ch.key()))
                coords.append(self.coordsfromchapterkey(ch))
                
        self.response.out.write( json.dumps({ 'chapternames' : chapternames, 'chapterkeys' : chapterkeys, 'coords' : coords }) )
                
    def coordsfromchapterkey(self,chapter):
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
                countycoordsdata[s] = helpers.prepcoordsfile('data/' + s + '/county/complex.txt')
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
                zipcoordsdata[s] = helpers.prepcoordsfile('data/' + s + '/zip/complex.txt')
                coords = helpers.getcoordsfromindex(zipcoordsdata[s], zipind)
            
            if coords:
                c.append(map(' '.join,coords))
        
        return c

class RegionsUpdate(webapp2.RequestHandler):
    def get(self):
        pass
    
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
    def get(self):
        pass
            
    
    def post(self):
        regionkey = self.request.get('regionkey')
        statecode = self.request.get('statecode')
        
        #get Region from db
        region = models.getregion(regionkey)
        #print region.to_xml()
        
        #get all chapters in the state
        
        chapters = models.getchaptersinstate(statecode)
        for chapter in chapters:
            newchapter = models.Chapter(parent=region.key())
            newchapter.name = chapter.name
            newchapter.state = chapter.state
            newchapter.zips = chapter.zips
            newchapter.zipinds = chapter.zipinds
            newchapter.counties = chapter.counties
            newchapter.countyinds = chapter.countyinds
            
            newchapter.put()
            models.deletechapterentry(chapter.key())
        
        #self.redirect('/chapters')
        self.response.out.write( json.dumps({ 'regionkey' : regionkey }) )
       
        
class Chapters(webapp2.RequestHandler):
    def get(self):
        regions = models.getallregions()
        template_values = {}
        #add regions to the payload
        template_values['regions'] = regions
        
        if self.request.get('chapterkey'): #if we've selected a specific chapter
            chapterkey = self.request.get('chapterkey')
            chapter = models.getchapter(chapterkey)
            template_values['chapter'] = chapter #add the chapter to the payload
        
        #if a region has been selected
        if self.request.get('regionkey'):
            regionkey = self.request.get('regionkey')
            
            if regionkey == 'unassigned': #if we selected the unassigned category
                selectedtab = 'unassigned'
                template_values['selectedtab'] = selectedtab
                
                chapters = models.getallchapters()
                chaptersworegion = []
                for chapter in chapters:
                    if not chapter.parent():
                        chaptersworegion.append(chapter)
                        #print chapter.name
                        #print chapter.parent().name
                        #print chapter.parent()
                    #print chapter.to_xml()
                #return
                chapters = chaptersworegion
            else: #if we've selected a region
                region = models.getregion(regionkey)
                
                chapters = models.getchaptersinregion(region)
                
                template_values['regionobj'] = region
             
            #template_values = { 'selectedtab' : region, 'chapters' : chapters, 'regions' : regions }
        else: #if we selected all
            chapters = models.getallchapters()
            selectedtab = "all"
            template_values['selectedtab'] = selectedtab
        
            #check to see if we're highlighting a particular chapter
            #else:
            #template_values = { 'chapters' : chapters, 'regions' : regions }
        
        template_values['chapters'] = chapters
        #for c in chapters:
        #    print c.state
        #return 
        #print template_values.keys()
        #print template_values.values() 
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
        else: chapter.zips = []
        
        if counties: chapter.counties = map(helpers.mapstrip, counties.split(","))
        else: chapter.counties = []
        
        countyindexdata = {}
        chapter.countyinds = []
        for county in chapter.counties:
            s = helpers.stateforcounty(county, chapter.state)
            countyname = county.split("|")[0]
            try:
                dataarr = countyindexdata[s]
                ind = helpers.findcountyindex(dataarr, countyname)
            except KeyError:
                #add dataarr to dict of state data arrays
                countyindexdata[s] = helpers.prepindexfile('data/' + s + '/county/simple.txt')
                ind = helpers.findcountyindex(countyindexdata[s], countyname)
            
            if not isinstance(ind,str):
                self.response.out.write(self.errorstr(ind))
                return
            
            chapter.countyinds.append(ind+'|'+s)
            
        zipindexdata = {}
        chapter.zipinds = []
        for zipcode in chapter.zips:
            s = helpers.stateforzip(zipcode,chapter.state)
            zipname = zipcode.split("|")[0]
            try:
                dataarr = zipindexdata[s]
                ind = helpers.findzipindex(dataarr,zipname)
            except KeyError:
                zipindexdata[s] = helpers.prepindexfile('data/' + s + '/zip/simple.txt')
                ind = helpers.findzipindex(zipindexdata[s], zipname)
                
            if not isinstance(ind,str):
                self.response.out.write(self.errorstr(ind))
                return
            
            chapter.zipinds.append(ind+'|'+s)
                
        chapter.put()
        
        self.redirect('/chapters')
        
    def errorstr(self,errorobj):
        return """
            Update Error: %s -- %s. Please hit the Back button in your browser and try again. Check your spelling and check the state of the invalid zipcode or county.
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
        
class Test(webapp2.RequestHandler):
    def get(self):
        states = models.getallstates()
        for state in states:
            print state.to_xml()
        
app = webapp2.WSGIApplication([
                               ('/', Maps),
                               ('/map', Maps),
                               ('/chapters', Chapters),
                               ('/chapters/update',ChaptersUpdate),
                               ('/chapters/create/auto', ChaptersCreateAuto),
                               ('/chapters/clear', ChaptersClear),
                               ('/chapters/delete', ChaptersDelete),
                               ('/regions/create', RegionsUpdate),
                               ('/regions/add-state', RegionsAddState),
                               ('/test', Test)]
                              ,debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == "__main__":
    main()