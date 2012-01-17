def genindfilenamearr(states):
    countyfilenamearr = []
    zipfilenamearr = [] 
    for s in states:
        countyfilename = 'data/' + s + '/county/simple.txt'
        zipfilename = 'data/' + s + '/zip/simple.txt'
        
        countyfilenamearr.append(countyfilename)
        zipfilenamearr.append(zipfilename)
               
    return { "county" : countyfilenamearr, "zip" : zipfilenamearr }

def mapstrip(s): return s.strip()
def quotekill(s): return s.replace('\"','').split()
def findcountyindicies(dataarr,countylist):
    inds = []
    for c in countylist:
        c = c.strip().split()
        try:
            found = dataarr.index(c)
            index = dataarr[found-3][0]
            inds.append(index)
        except ValueError:
            return { 'error' : 'County Not Found' , 'baditem' : c }
        
    return inds

def findzipindicies(dataarr,ziplist):    
    inds = []
    for z in ziplist:
        try:
            found = dataarr.index([z])
            index = dataarr[found-1][0]
        except ValueError:
            return { 'error' : 'Zipcode Not Found', 'baditem' : z }
            
        inds.append(index)
        
    return inds

def getdatafilearray(filename):
    f = open(filename)
    data = f.readlines()
    f.close()
    
    return data

def spacekill(s): return s!=''
def mapkill(line): return filter(spacekill,line.split())
def getcoordsfromindex(dataarr,ind):
    starti = 0
    while( starti <= len(dataarr)-1 ):
        endi = dataarr.index(['END'],starti)
        key = dataarr[starti][0]
        coords = dataarr[starti+1:endi]
        if key == ind:
            return coords
        
        starti = endi+1
        
    return None

def commakill(s): return s.replace(',','').split()
def chapterstojson(dataarr):
    starti = 0
    d = {}
    while(starti<=len(dataarr)-1):
        endi = dataarr.index([],starti)
        chaptername = ' '.join(dataarr[starti])
        chaptercounties = dataarr[starti+1]
        chapterzips = dataarr[starti+2]
        d[chaptername] = [chaptercounties,chapterzips]
        
        starti = endi+1
        
    return d