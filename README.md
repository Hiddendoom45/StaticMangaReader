# StaticMangaReader

Used to Generate some basic html/javascript to read manga from a static website. The resulting files can be used in any sort of static web hosting provider or viewed locally from your computer.

The javascript generated is designed to be compatabile with older browsers (tested with a 2013 browser).

### Usage

The main script is a python program that generates the pages needed to view the images of downloaded manga. Compatible with both python2 and python3. 

basic format
```
python generate.py  directory
```
directory - the directory containing the chapters of the manga in the following form
```
directory
|
| -- chapter1
|  |
|  | -- page1.png
|  | -- page2.png
|
| -- chapter2
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- page3.png
```
Default usage will generate the index files within the chapter directory i.e. chapter1/index.html
Chapters will be chained together based on the lexical ordering of the chapter folders. So the last page of chapter1 will link to the first page of chapter2.

## Options

#### --index [image,chapters,numbered] 

Specifies the way in which the index pages will be generated. Default is image.

Image genrates the json file with the page names and the index files in the same directory as the images.
```
directory
|
| -- chapter1
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- index.html
|
| -- chapter2
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- page3.png
|  | -- index.html
```

Chapters will name the index pages with the same names as each chapter folder 
```
directory
|
| -- chapter1
|  |
|  | -- page1.png
|  | -- page2.png
|
| -- chapter1.html
|
| -- chapter2
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- page3.png
|
| -- chapter2.html
```
Numbered will use the occurance number to name the index files instead
```
directory
|
| -- chapter1
|  |
|  | -- page1.png
|  | -- page2.png
|
| -- 1.html
|
| -- chapter2
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- page3.png
|
| -- 2.html
```

#### --clean

Removes all files that would've been generated with the given parameters as well as any empty folders left by the removals.

#### --no-page

Use reader.js instead of pagedreader.js results in only one history entry per chapter instead of one per page.

#### --jsdir

Specifies the location to put the javascript file. Paths are relative to the main directory

i.e. to place the javascript file within a resources folder that is located within the parent of the chapter folder

```
python generate.py directory --jsdir ../res/js
```

#### --indexdir

Shifts the locations of the index files so their relative position to the specified directory is the same as their relative position to the main directory without specifying this. In most cases the index files will be placed directly in the folder with the exception of the default `--index image` generation. Paths are relative to the main directory.

i.e. moving the index files to their parent with `python generate.py directory --indexdir ../`

```
parent
|
| -- directory
|  |
|  | -- chapter1
|  |  |
|  |  | -- page1.png
|  |  | -- page2.png
|  |
|  | -- chapter2
|  |  |
|  |  | -- page1.png
|  |  | -- page2.png
|  |  | -- page3.png
|
| -- chapter1
|  |
|  | -- index.html
| 
| -- chapter2
|  |
|  | -- index.html
```

#### --home

Specifies the directory to put the home file that contains an overview of all chapters. By default the file is named index.html and is placed in the main directory. Paths are relative to the main directory.

#### --nohome

Avoids generating the home file, chapters will still link to the home file directory.

#### --chlist

A file with the list of all chapters relative to the main directory or absolute paths. Can be used to specify a specific ordering of chapters. Ignores folders that do not exist.

#### --pagelist

A file with a list of all pages relative to each chapter directory or the main directory. Can be used to specify page ordering. Ignores files that do not exist.

#### --usejson

Generates a json file with all pages, and relative reference to previous and next file. Will prevent site from working locally without a server.

#### --long

Generates in long-strip format where all pages in a chapter are placed one after another in one long strip. Ignores the paging, and usejson arguments.


#### --nojs

Generates the page with no javascript. This has no effect if the long argument is used and ignores the paging option.

#### --chext

Changes the extension of indexed images, useful if images are stored on the server in compressed form but requested as images. i.e. `--chext "lep,jpg"` converts images stored in the lepton format to reference the .jpg url.


#### --oneshot

Use for oneshot mangas/single chapters. The directory parameter specifies the location of the chapter's pages rather than the directory containing the chapter folders. 

```
directory
|
| -- page1.png
| -- page2.png
```
