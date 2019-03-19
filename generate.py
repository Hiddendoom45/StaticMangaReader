import argparse
import os
import os.path as path
import json
import shutil
import sys
import io

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
parser.add_argument('--usejson',action='store_true',help="generates json with pages")
args = parser.parse_args()
directory = args.directory[0]

#determine generators
chdirectchild = lambda dir : [f for f in os.listdir(dir) if path.isdir(path.join(dir,f))]
chfromlist = lambda dir: [ path.join(directory,f) if not f.startswith('/') else f for f in args.chlist.read().splitlines()]
if args.chlist is not None:
    chgen = chfromlist
else:
    chgen = chdirectchild

if args.indexdir is None:
    inddir = directory
else:
    inddir = path.join(directory,args.indexdir)
if sys.version_info < (3,0):
    if not path.exists(inddir):
        os.makedirs(inddir)
else:
    os.makedirs(inddir,exist_ok=True)
indwithimg = lambda dir,ch : [ path.join(inddir,c,"index.html") for c in ch]
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

htmltemplatenginx = "<!DOCTYPE html><html><head><link rel=\"preload\" href=\"$JS$\" as=\"script\"><title>$TITLE$</title></head><body onload=\"loadJSON()\"><script>$CUSTOMJS$</script><script type=\"text/javascript\" src=\"$JS$\"></script><img id=\"mainimage\" href=\"#\" style=\"width:100%\"src=\"$IMAGE$\" onclick=\"nextPage()\" loadeddata=\"scrollTop()\" $HIDDEN$></img><div id=\"pagination\" style=\"position: relative\"><button style=\"float:left;width:20%;height:3em\"type=\"button\" onclick=\"previousPage()\">&lt;==</button><span style=\"margin:auto; position:absolute;left: 30%;width: 40%;text-align: center;\"> <input type=\"number\" name=\"pageField\" id=\"pageField\" style=\"text-align:left;width: 4em\" onchange=\"setpage(value-1)\" value=\"1\">/ <span id=\"total\"> </span></span><span style=\"margin:auto; position:absolute;left: 20%;width: 60%;text-align: center;top: 1em;word-wrap: break-word;\"><a href=\"$HOME$\">$TITLE$</a></span><button style=\"float:right;width:20%;height:3em\" type=\"button\" onclick=\"nextPage()\">==&gt;</button></div></body></html>"

htmltemplate = htmltemplatenginx
hometemplate = "<!DOCTYPE html><html><head> <meta charset=\"utf-8\"/> <title>$TITLE$</title></head><body> <ul> $CHAPLIST$ </ul></body></html>"

#whether to use paged reader or non-paged reader
page = args.page
#copy js
if page:
    reader = "pagedreader.js"
else:
    reader = "reader.js"
reader = path.join(path.split(path.realpath(__file__))[0],reader)
if args.jsdir is not None:
    jsdir = path.join(directory,args.jsdir)
else:
    jsdir = directory

smkdirs(jsdir)
js = path.join(jsdir,path.split(reader)[1])
if args.clean:
    sremove(js)
else:
    shutil.copyfile(reader,js)

homefile = path.join(directory,args.home,"index.html" if not args.nohome else "")
chaplist = []

for i in range(len(chapters)):
    #directory containing the pages for all the chapters
    chdir = path.join(directory,chapters[i])
    pages = [ path.relpath(path.join(chdir,f),path.split(indexes[i])[0]) for f in os.listdir(chdir) if (path.isfile(path.join(chdir,f)) and not f.endswith("chapters.json") and not f.endswith("index.html"))]
    if sys.version_info < (3,0):
        chap = "<li><a href=\"%s\">%s</a></li>" % (path.relpath(indexes[i],path.split(homefile)[0]),chapters[i])
    else:
        chap = "<li><a href=\"{}\">{}</a></li>".format(path.relpath(indexes[i],path.split(homefile)[0]),chapters[i])
    chaplist.append(chap)
    #generate json
    data = {}
    if (i<len(chapters)-1):
         data['nextchapter'] = path.relpath(indexes[i+1],path.split(indexes[i])[0])
    else:
        data['nextchapter'] = "#"
    
    if (i>0):
        data['previouschapter'] = path.relpath(indexes[i-1],path.split(indexes[i])[0])
    else:
        data['previouschapter'] = "#"
    
    data['pages'] = [ {"page":p} for p in pages ]
    if args.usejson:
        jsfp = path.join(path.split(indexes[i])[0],path.relpath(chjson[i],path.split(indexes[i])[0]))
        smkdirsf(jsfp)
        if args.clean:
            sremove(jsfp)
        else:
            with open(jsfp,"w") as jsonfile:
                uniwrite(jsonfile,json.dumps(data))
    #generate html
    if args.clean:
        sremove(indexes[i])
    else:
        smkdirsf(indexes[i])
        with io.open(indexes[i],"w",encoding='utf-8') as htmlfile:
            html=htmltemplate
            #replace various part of template with generated strings
            html = html.replace("$TITLE$",chapters[i])
            html = html.replace("$IMAGE$",data['pages'][0]['page'])
            html = html.replace("$JS$",path.relpath(js,path.split(indexes[i])[0]))
            html = html.replace("$HIDDEN$", "hidden=\"true\"" if page else "")
            html = html.replace("$CUSTOMJS$",("chjson=\""+path.relpath(chjson[i],path.split(indexes[i])[0])+"\"" if args.usejson else "data="+json.dumps(data)))
            html = html.replace("$HOME$",path.relpath(homefile,path.split(indexes[i])[0]))    
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