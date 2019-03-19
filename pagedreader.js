//identical to the reader except forces page reload to a new url for each page, allows moving via history
var currentpage = 0;
var preload
function loadJSON() {
	if(typeof chjson === 'undefined') {
		setup()
	}
	else {
		var xobj = new XMLHttpRequest();
		xobj.overrideMimeType("application/json");
		xobj.open('GET', chjson, true);
		xobj.onreadystatechange = function () {
			if (xobj.readyState == 4 && xobj.status == "200") {
				data = JSON.parse(xobj.responseText);
				setup();
			}
		};
	}
	xobj.send(null);  
}
function setup() {
	chapters = data.pages;
	document.getElementById('total').innerHTML = " "+data.pages.length
	var pagenum = getParameterByName("page")
	if(pagenum==="end"){
		setpage(chapters.length);
	}
	else if(Number.isInteger(parseInt(pagenum))){
		setpage(parseInt(pagenum)-1);
	}
	else{
		setpage(0);
	}
	document.getElementById('mainimage').hidden=false;
	if(currentpage<chapters.length-2){
		(new Image()).src = chapters[currentpage+1].page
	}
}
function nextPage() {
	if(typeof chapters === 'undefined') return;
	if(currentpage>=chapters.length-1){
		window.location = data.nextchapter
	}
	else{
		window.location="index.html?page="+(++currentpage+1);
		preload = ((new Image()).src = chapters[currentpage].page)
	}
}
function previousPage() {
	if(typeof chapters === 'undefined') return;
	if(currentpage>0){
		window.location="index.html?page="+(--currentpage+1)
	}
	else{
		window.location = data.previouschapter+"?page=end"
	}
}
function setpage(page) {
	if(typeof chapters === 'undefined') return;
	if(page<0) page = 0;
	if(page>=chapters.length) page = chapters.length-1
	currentpage = page;
	document.getElementById('mainimage').src=chapters[page].page
	document.body.scrollTop = document.documentElement.scrollTop = 0;
	document.getElementById('pageField').value=currentpage+1
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