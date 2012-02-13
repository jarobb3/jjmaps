import webapp2
import os
import models
import helpers
import json
import pprint

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Test(webapp2.RequestHandler):
    def get(self):
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
            
        self.response.out.write( json.dumps({ 'chapters' : chaptersdict }) )
        
app = webapp2.WSGIApplication([('/test', Test)]
                              ,debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == "__main__":
    main()