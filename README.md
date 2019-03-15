# StaticMangaReader

Used to Generate some basic html/javascript to read manga from a static website. The resulting files can be used in any sort of static web hosting provider.



Note: Current form only works with a webserver, except on firefox, compatability for local reading will be added.
Testing is done with nginx as the static webserver.

### Usage

The main script is a python program that generates the pages needed to view the images of a downloaded manga. Compatible with both python2 and python3. 

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

Specifies the way in which the index pages will be generated. Default is index.

Index genrates the json file with the page names and the index files in the same directory as the images.
```
directory
|
| -- chapter1
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- index.html
|  | -- chapters.json
|
| -- chapter2
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- page3.png
|  | -- index.html
|  | -- chapters.json
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
| -- chapter1.json
|
| -- chapter2
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- page3.png
| -- chapter2.html
| -- chapter2.json
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
| -- 1.json
|
| -- chapter2
|  |
|  | -- page1.png
|  | -- page2.png
|  | -- page3.png
| -- 2.html
| -- 2.json
```

#### --paging

This will specify the use of pagedreader.js instead of reader.js which loads a new url for each page appending a ?page=# query to the end of the index page. This is slightly slower than the default which simply changes the main image's source but results in each page being recorded separately in your browser's history. 