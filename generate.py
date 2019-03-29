import argparse
import os
import os.path as path
import json
import shutil
import sys
import io

if sys.version_info < (3,0):
    from urllib import pathname2url
else:
    from urllib.request import pathname2url

#helper functions
def dremove(dir):
    if len(os.listdir(dir)) == 0:
        os.rmdir(dir)
        dremove(path.split(dir)[0])
def sremove(f):
    try:
        os.remove(f)
        dremove(path.split(f)[0])
    except OSError:
        pass 
#file opened with encode unicode
def uniwrite(f,str):
    if sys.version_info < (3,0):
        f.write(unicode(str,'utf-8'))
    else:
        f.write(str)
def smkdirsf(f):
    smkdirs(path.split(f)[0])

def smkdirs(dir):
    if sys.version_info < (3,0):
        if not path.exists(dir):
            os.makedirs(dir)
    else:
        os.makedirs(jsdir,exist_ok=True)
def urlpathrel(topath,currentpath):
    return pathname2url(path.relpath(topath,path.split(currentpath)[0]))
def pagepath(pagenum,index):
    pagenum += 1
    p =  path.join(path.split(index)[0],str(pagenum)+".html") if args.index == 'image' else ".".join(index.split(".")[:-1])+"_"+str(pagenum)+".html"
    return p

def rfile(f):
    with open(f,'r') as ofile:
        return ofile.read()
#setup parser and parse arguments
parser = argparse.ArgumentParser(description='Generates a static manga site from some images')
parser.add_argument('directory',nargs=1,help="The directory containing all the chapter folders")
parser.add_argument('--page','-p',default=False,action='store_const',const=True,help="Uses pagination such that each page generates a new url")
parser.add_argument('--jsdir',help="The relative path to directory for the js file relative to the main directory")
parser.add_argument('--indexdir',help="The relative path to directory for the index fields relative to the main directory")
parser.add_argument('--index',choices=['image','chapters','numbered'],default='image',help="Determines how the site pages are generated.")
parser.add_argument('--home',default="",help="The home directory containing an overview of all chapters")
parser.add_argument('--nohome',action='store_true',help="Prevents creation of home page for the manga")
parser.add_argument('--clean',action='store_true',help="Removes files that would've been generated with the given parameters")
parser.add_argument('--chlist',help="File containing the chapters")
parser.add_argument('--pagelist',help="File containing the pages within a chapter folder")
parser.add_argument('--usejson',action='store_true',help="generates json with pages")
parser.add_argument('--long',action='store_true',help="Use long strip format to display chapters")
parser.add_argument('--nojs',action='store_true',help="Do not use any javascript in the generated files")
args = parser.parse_args()
directory = args.directory[0]

#determine generators
chdirectchild = lambda dir : [f for f in os.listdir(dir) if path.isdir(path.join(dir,f))]
chfromlist = lambda dir: [ path.join(directory,f) if not path.isabs(f) else f for f in rfile(args.chlist if path.isabs(args.chlist) else path.join(directory,args.chlist)).splitlines()]
if args.chlist is not None:
    chgen = chfromlist
else:
    chgen = chdirectchild

if args.indexdir is None:
    inddir = directory
else:
    inddir = args.indexdir if path.isabs(args.indexdir) else path.join(directory,args.indexdir)
if sys.version_info < (3,0):
    if not path.exists(inddir):
        os.makedirs(inddir)
else:
    os.makedirs(inddir,exist_ok=True)
indwithimg = lambda dir,ch : [path.join(inddir,c,"index.html") for c in ch]
indseparate = lambda dir,ch : [path.join(inddir,c+".html") for c in ch]
indnumbered = lambda dir,ch : [path.join(inddir,str(i+1)+".html") for i in range(len(ch))]

jsonwithindex = lambda dir,ch,ind : [ path.join(path.split(i)[0],"chapters.json") for i in ind]
jsonindexname = lambda dir,ch,ind : [ ".".join(i.split(".")[:-1])+".json" for i in ind]

#generators for each thing
if args.index=='image':
    generator = (chgen,indwithimg,jsonwithindex)
elif args.index=='chapters':
    generator = (chgen,indseparate,jsonindexname)
elif args.index=='numbered':
    generator = (chgen,indnumbered,jsonindexname)
# list of chapter directories
chapters = generator[0](directory)
#list of index files
indexes= generator[1](directory,chapters)
#json files
chjson= generator[2](directory,chapters,indexes)

#read from template file
htmltemplatefile = ("template.html" if not args.nojs else "nojstemplate.html") if not args.long else "longtemplate.html"
htmltemplatefile = path.join(path.split(path.realpath(__file__))[0],htmltemplatefile)
with open(htmltemplatefile,'r') as htmlfile:
    htmltemplate = htmlfile.read()

hometemplatefile = path.join(path.split(path.realpath(__file__))[0],"hometemplate.html")
with open(hometemplatefile,'r') as htmlfile:
    hometemplate = htmlfile.read()

nptemplatefile = path.join(path.split(path.realpath(__file__))[0],"nopagetemplate.html")
with open(nptemplatefile,'r') as htmlfile:
    nptemplate = htmlfile.read()

#whether to use paged reader or non-paged reader
page = args.page
#copy js
if page:
    reader = "pagedreader.js"
else:
    reader = "reader.js"
reader = path.join(path.split(path.realpath(__file__))[0],reader)
if args.jsdir is not None:
    jsdir = args.jsdir if path.isabs(jsdir) else path.join(directory,args.jsdir)
else:
    jsdir = directory

smkdirs(jsdir)
js = path.join(jsdir,path.split(reader)[1])
if not args.long and not args.nojs:
    if args.clean:
        sremove(js)
    else:
        shutil.copyfile(reader,js)

homefile = path.join( args.home if path.isabs(args.home) else path.join(directory,args.home),"index.html" if not args.nohome else "")
chaplist = []

#Stuff for long strip
lpagetemplate = "<a href=\"$HREF$\"><img src=\"$SRC$\" id=\"$ID$\" style=\"width:100%;\"></img></a>"
def genimglist(pages,nextchapter):
    l = []
    for i in range(len(pages)):
        tlpagetemplate = lpagetemplate.replace("$SRC$",pages[i]['page'])
        tlpagetemplate = tlpagetemplate.replace("$ID$",".".join(pages[i]['page'].split(".")[:-1]))

        if i == len(pages)-1:
            l.append(tlpagetemplate.replace("$HREF$",nextchapter))
        else:
            l.append(tlpagetemplate.replace("$HREF$","#"+".".join(pages[i+1]['page'].split(".")[:-1])))
    return l

lastpage = None

for i in range(len(chapters)):
    #directory containing the pages for all the chapters
    chdir = path.join(directory,chapters[i])
    if args.pagelist is None:
        pages = [ path.relpath(path.join(chdir,f),path.split(indexes[i])[0]) for f in os.listdir(chdir) if (path.isfile(path.join(chdir,f)) and not f.endswith(".json") and not f.endswith(".html"))]
    else:
        with open(path.join(chdir,args.pagelist),'r') as pagefile:
            pages = pagefile.readlines()
    if sys.version_info < (3,0):
        chap = "<li><a href=\"%s\">%s</a></li>" % (urlpathrel(indexes[i],homefile),path.split(chapters[i])[1])
    else:
        chap = "<li><a href=\"{}\">{}</a></li>".format(urlpathrel(indexes[i],homefile),path.split(chapters[i])[1])
    chaplist.append(chap)
    #generate json
    data = {}
    if (i<len(chapters)-1):
         data['nextchapter'] =  urlpathrel(indexes[i+1],indexes[i])
    else:
        data['nextchapter'] = "#"
    
    if (i>0):
        data['previouschapter'] = urlpathrel(pagepath(lastpage,indexes[i-1]),indexes[i]) if args.nojs and not lastpage<=1 else urlpathrel(indexes[i-1],indexes[i])
    else:
        data['previouschapter'] = "#"
    
    data['pages'] = [ {"page":p} for p in pages ]
    lastpage = len(data['pages']) - 1
    if len(data['pages'])==0:
        if args.clean:
            if args.index=="image" and inddir == directory:
                try:
                    os.remove(indexes[i])
                except OSError:
                    pass
            else:
                sremove(indexes[i])
            
        else:
            smkdirsf(indexes[i])
            with io.open(indexes[i],'w',encoding='utf-8') as htmlfile:
                html = nptemplate
                html = html.replace("$TITLE$", path.split(chapters[i])[1])
                html = html.replace("$HOME$", urlpathrel(homefile,indexes[i]))
                html = html.replace("$NEXT$", data['nextchapter'])
                html = html.replace("$PREV$", data['previouschapter']+("?page=end" if not args.nojs and not args.long else ""))
                html = html.replace("$TOTAL$", "0")
                html = html.replace("$CURRENT$", "0")
                uniwrite(htmlfile,html)
        continue
    if args.usejson and not args.nojs:
        jsfp = path.join(path.split(indexes[i])[0],path.relpath(chjson[i],path.split(indexes[i])[0]))
        smkdirsf(jsfp)
        if args.clean:
            sremove(jsfp)
        else:
            with open(jsfp,"w") as jsonfile:
                uniwrite(jsonfile,json.dumps(data))
    #generate html
    #nojs template
    if args.nojs:
        if args.clean:
            for p in range(len(data['pages'])):
                sremove(pagepath(p,indexes[i]))
        else:
            smkdirsf(indexes[i])
            
            for p in range(len(data['pages'])):
                # use differnt join method if index form
                ppath = pagepath(p,indexes[i])
                with io.open(ppath,'w',encoding='utf-8') as htmlfile:
                    html=htmltemplate
                    #replace various part of template with generated strings
                    html = html.replace("$TITLE$",path.split(chapters[i])[1])
                    html = html.replace("$IMAGE$",data['pages'][p]['page'])
                    html = html.replace("$PRELOAD$",data['pages'][p+1]['page'] if p < len(data['pages'])-1 else "#")
                    html = html.replace("$HOME$",urlpathrel(homefile,ppath))
                    html = html.replace("$CURRENT$",str(p+1))
                    html = html.replace("$NEXT$", urlpathrel(pagepath(p+1,indexes[i]),ppath)if p < len(data['pages'])-1 else data['nextchapter'])
                    html = html.replace("$PREV$",data['previouschapter'] if p == 0 else urlpathrel(pagepath(p-1,indexes[i]),ppath))
                    html = html.replace("$PAGES$", "".join(genimglist(data['pages'],data['nextchapter'])) )
                    html = html.replace("$TOTAL$",str(len(pages)))
                    uniwrite(htmlfile,html)
            data['nextchapter']=urlpathrel(pagepath(1,indexes[i]),ppath) if len(data['pages'])>1 else data['nextchapter']

    #generic template
    if args.clean:
        sremove(indexes[i])
    else:
        smkdirsf(indexes[i])
        with io.open(indexes[i],"w",encoding='utf-8') as htmlfile:
            html=htmltemplate
            #replace various part of template with generated strings
            html = html.replace("$TITLE$",path.split(chapters[i])[1])
            html = html.replace("$IMAGE$",data['pages'][0]['page'])
            html = html.replace("$JS$",path.relpath(js,path.split(indexes[i])[0]))
            html = html.replace("$HIDDEN$", "hidden=\"true\"" if page else "")
            html = html.replace("$CUSTOMJS$",("chjson=\""+path.relpath(chjson[i],path.split(indexes[i])[0])+"\"" if args.usejson else "data="+json.dumps(data)))
            html = html.replace("$HOME$",pathname2url(path.relpath(homefile,path.split(indexes[i])[0])))
            html = html.replace("$NEXT$",data['nextchapter'])
            html = html.replace("$PREV$",data['previouschapter'])
            html = html.replace("$PAGES$", "".join(genimglist(data['pages'],data['nextchapter'])) )
            html = html.replace("$TOTAL$",str(len(pages)))
            html = html.replace("$CURRENT$","1")
            uniwrite(htmlfile,html)

if not args.nohome:
    if args.clean:
        sremove(homefile)
    else:
        smkdirsf(homefile)
        with io.open(homefile,'w',encoding='utf-8') as homefile:
            home = hometemplate
            home = home.replace("$CHAPLIST$","".join(chaplist))
            home = home.replace("$TITLE$","Chapter Overview")
            uniwrite(homefile,home)