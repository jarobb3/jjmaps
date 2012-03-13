import webapp2
import os
import models
import helpers
import json
#import pprint

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
        
class Chapters(webapp2.RequestHandler):
    def unassignedchapters(self):
        chapters = models.getallchapters()
        chaptersworegion = []
        for chapter in chapters:
            if not chapter.parent():
                chaptersworegion.append(chapter)
                
        return chaptersworegion
    
    def assignedchapters(self, region):
        return models.getchaptersinregion(region)
    
    def allchapters(self):
        return models.getallchapters()
    
    def get(self):
        tab = self.request.get('tab')
        if not tab:
            tab = 'all'
        #show all, unassigned, and every region on the page, use display none on the front end to show one list at time
        allchapters = models.getallchapters()
        unassignedchapters = self.unassignedchapters()
        
        regions = models.getallregions()
        
        regionswchapters = {}
        for r in regions:
            #get the chapter list for each region
            
            chs = models.getchaptersinregion(r)
            chaptersdict = []
            for c in chs:
                chapterkey = c.key()
                chapterdict = models.to_dict(c)
                chapterdict['key'] = str(chapterkey)
                chaptersdict.append(chapterdict)
                
            regionswchapters[r.name] = chaptersdict
            
        template_values = {
            'regions' : regions,
            'chaptersbyregion' : regionswchapters,
            'allchapters' : allchapters,
            'unassignedchapters' : unassignedchapters,
            'tabname' : tab
        }  
        
        path = os.path.join(os.path.dirname(__file__), 'templates/chapters.html')
        self.response.out.write(template.render(path, template_values))
        
        
class ChaptersEdit(webapp2.RedirectHandler):
    def post(self):
        chapterkey = self.request.get('chapterkey')
        chapter = models.getchapter(chapterkey)
        chapterdict = models.to_dict(chapter)
        
        self.response.out.write( json.dumps({ 'chapter' : chapterdict , 'chapterkey' : chapterkey }) )   
        
class ChaptersUpdate(webapp2.RequestHandler):
    def post(self):
        #query database to see if this entry already exists (query by chaptername and state)
        domain = 'http://jandj.gldnfleece.com/'
        
        if self.request.get('chapterkey'):
            chapter = models.getchapter(self.request.get('chapterkey'))
        else:
            region = models.getregionfromstate(self.request.get('chapterstate').upper())
            if region:
                chapter = models.Chapter(parent=region.key())
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
                countyindexdata[s] = helpers.prepindexfile(domain + 'data/' + s + '/county/simple.txt')
                ind = helpers.findcountyindex(countyindexdata[s], countyname)
            
            if not isinstance(ind,str):
                self.response.out.write(self.errorstr(ind))
                return
            
            chapter.countyinds.append(ind+'|'+s)
            
        zipindexdata = {}
        chapter.zipinds = []
        ziperrors = []
        for zipcode in chapter.zips:
            s = helpers.stateforzip(zipcode,chapter.state)
            zipname = zipcode.split("|")[0]
            try:
                dataarr = zipindexdata[s]
                ind = helpers.findzipindex(dataarr,zipname)
            except KeyError:
                zipindexdata[s] = helpers.prepindexfile(domain + 'data/' + s + '/zip/simple.txt')
                ind = helpers.findzipindex(zipindexdata[s], zipname)
                
            if not isinstance(ind,str):
                #self.response.out.write(self.errorstr(ind))
                ziperrors.append(zipcode)
                #return
            else:
                chapter.zipinds.append(ind+'|'+s)
                
        chapter.put()
        
        if len(ziperrors) == 0:
            self.redirect('/chapters')
        else:
            self.response.out.write(self.errorzips(ziperrors))
            return
            
    def errorstr(self,errorobj):
        return """
            Update Error: %s -- %s. Please hit the Back button in your browser and try again. Check your spelling and check the state of the invalid zipcode or county.
        """ % (errorobj['error'],"\""+errorobj['baditem']+"\"")
        
    def errorzips(self,errorziplist):
        return """
            Your chapter was created/updated, but we couldn't find a few zipcodes in our data files.
            Here's the list of zipcodes we couldn't find: <br /> %s <br /> <a href='/chapters'>Continue to Admin page</a>
            """ % ('<br />'.join(errorziplist))
        
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
        domain = 'http://jandj.gldnfleece.com/'
        
        chaptersdatafile = map(helpers.commakill,helpers.getdatafilearray(domain + 'data/' + state.upper() + '/chapters.txt'))
        chaptersjson = helpers.chapterstojson(chaptersdatafile)
        
        for chaptername in chaptersjson:
            chapterjson = chaptersjson[chaptername]
            
            chapter = models.Chapter()
            chapter.name = chaptername
            chapter.state = state.upper()
            
            #countyfilepath = 'data/' + state + '/county/simple.txt'
            chapter.counties = chapterjson[0]
            if chapter.counties[0] != 'Null':
                countydataarr = map(helpers.quotekill,helpers.getdatafilearray(domain + 'data/' + state + '/county/simple.txt'))
                chapter.countyinds = helpers.findcountyindicies(countydataarr, chapter.counties)
            else:
                chapter.countyinds = []
            
            #zipsfilepath = 'data/' + state + '/zip/simple.txt'
            chapter.zips = chapterjson[1]
            if chapter.zips[0] != 'Null':
                zipsdataarr = map(helpers.quotekill,helpers.getdatafilearray(domain + 'data/' + state + '/zip/simple.txt'))
                chapter.zipinds = helpers.findzipindicies(zipsdataarr, chapter.zips)
            else:
                chapter.zipinds = []
  
            chapter.put()
            
        self.redirect('/chapters')
        
class ChaptersChangeTab(webapp2.RequestHandler):
    def get(self):
        selectiontype = self.request.get('selectiontype')
        regionkey = self.request.get('regionkey')
        
        if selectiontype == 'all':
            chapters = models.getallchapters()
            print 'all'
        elif selectiontype == 'unassigned':
            chapters = models.getallchapters()
            chaptersworegion = []
            for chapter in chapters:
                if not chapter.parent():
                    chaptersworegion.append(chapter)
            
            chapters = chaptersworegion
            #print 'unassigned'
        elif selectiontype == 'region':
            chapters = models.getchaptersinregion(regionkey)
            #print 'region'
        else:
            chapters = []
            #print 'broken'
        
        chaptersarr = []
        for ch in chapters:
            chaptersarr.append(models.to_dict(ch))
        
        self.response.out.write( json.dumps({ 'chapters' : chaptersarr }) )   
    
    def post(self):
        selectiontype = self.request.get('selectiontype')
        regionkey = self.request.get('regionkey')
        
        if selectiontype == 'all':
            chapters = models.getallchapters()
        elif selectiontype == 'unassigned':
            chapters = models.getallchapters()
            chaptersworegion = []
            for chapter in chapters:
                if not chapter.parent():
                    chaptersworegion.append(chapter)
            
            chapters = chaptersworegion
        elif selectiontype == 'region':
            chapters = models.getchaptersinregion(regionkey)
        else:
            chapters = []
        
        chaptersarr = []
        for ch in chapters:
            chaptersarr.append(models.to_dict(ch))
        
        self.response.out.write( json.dumps({ 'chapters' : chaptersarr }) )   
        
        
app = webapp2.WSGIApplication([
                               ('/chapters', Chapters),
                               ('/chapters/edit', ChaptersEdit),
                               ('/chapters/update',ChaptersUpdate),
                               ('/chapters/create/auto', ChaptersCreateAuto),
                               ('/chapters/clear', ChaptersClear),
                               ('/chapters/delete', ChaptersDelete),
                               ('/chapters/change-tab', ChaptersChangeTab)]
                              ,debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == "__main__":
    main()