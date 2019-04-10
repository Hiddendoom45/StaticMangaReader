//identical to the reader except uses history to create new url for each page, allows moving via history
var currentpage = 0;
var preload = new Image();
function loadJSON() {
    document.getElementById('mainimage').addEventListener('load',() => {
        document.body.scrollTop = document.documentElement.scrollTop = 0;
    });
    window.addEventListener('popstate',(event) => {
        if(event.state==null) setpage(0,true)
        else setpage(event.state.page,true)
    })
    if(typeof chjson === 'undefined'){
        setup();
    }
    else{
        var xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
        xobj.open('GET', chjson, true);
        xobj.onreadystatechange = function () {
        if (xobj.readyState == 4 && xobj.status == "200") {
            data = JSON.parse(xobj.responseText);
            setup();
        }
        };
        xobj.send(null);
    }
}
function setup(){
    chapters = data.pages;
    document.getElementById('total').innerHTML = " "+data.pages.length
    var pagenum = getParameterByName("page");
    if(pagenum==="end"){
        setpage(chapters.length,true);
    }
    else if(!isNaN(parseInt(pagenum))){
        setpage(parseInt(pagenum)-1,true);
    }
}
function nextPage() {
    if(typeof chapters === 'undefined') return;
    if(currentpage>=chapters.length-1){
       if(data.nextchapter!=='') window.location = data.nextchapter;
    }
    else{
        setpage(++currentpage);
    }
}
function previousPage() {
    if(typeof chapters === 'undefined') return;
    if(currentpage>0){
        setpage(--currentpage);
    }
    else{
        if(data.previouschapter!=='') window.location = data.previouschapter+"?page=end";
    }
}
function setpage(page,ishistory=false) {
    if(typeof chapters === 'undefined') return;
    if(page<0) page = 0;
    if(page>=chapters.length) page = chapters.length-1;
    currentpage = page;
    document.getElementById('mainimage').src=chapters[page].page;
    document.getElementById('pageField').value=currentpage+1;
    if(currentpage<chapters.length-1)preload.src = chapters[currentpage+1].page;
    if(!ishistory)history.pushState({page:currentpage},"","?page="+(currentpage+1));
    else history.replaceState({page:currentpage},"","?page="+(currentpage+1));
}
function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}