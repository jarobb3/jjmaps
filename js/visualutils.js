function addClass(elem,className){
	elem.className += " "+className;
}

function removeClass(elem,className){
	var reg = new RegExp('(\\s|^)' + className + '(\\s|$)');
	elem.className = elem.className.replace(reg, '' )
}

function showOverlay(){
	var overlay = document.getElementById('overlay');
	removeClass(overlay,'hidden');
}

function hideOverlay(){
	var overlay = document.getElementById('overlay');
	addClass(overlay,'hidden');
}

function getColor(){
	transparency = '180';
	/*colors = [transparency+',141,211,199',
	          transparency+',190,186,218',
	          transparency+',251,128,114',
	          transparency+',128,177,211',
	          transparency+',253,180,98',
	          transparency+',179,222,105',
	          transparency+',252,205,229',
	          transparency+',255,255,179'];
	*/
	var colors = ['228,26,28',
	              '55,126,184',
	              '77,175,74',
	              '152,78,163',
	              '255,127,0',
	              '255,255,51',
	              '166,86,40',
	              '247,129,191'];
	/*var colors = ['166,206,227',
	              '31,120,180',
	              '178,223,138',
	              '51,160,44',
	              '251,154,153',
	              '227,26,28',
	              '253,191,111',
	              '255,127,0',
	              '202,178,214',
	              '106,61,154'];*/
	var index = (numChaptersAdded-1)%8;
	var color = transparency+','+colors[index];
	
	return color;
}

function createLegend(chapterkey){
	var color = getColor().split(',');
	
	var legend = document.getElementById(chapterkey+'-legend');
	var rawcolor = color.slice(1).join(',');
	legend.style.backgroundColor = 'rgb('+rawcolor+')';
	removeClass(legend,'hidden');
	
	return color;
}

function showLegend(chapterkey){
	var legend = document.getElementById(chapterkey+'-legend');
	removeClass(legend,'hidden');
}

function hideLegend(chapterkey){
	var legend = document.getElementById(chapterkey+'-legend');
	addClass(legend,'hidden');
}

function showAction(actionname,chapterkey){
	var elem = document.getElementById(chapterkey+'-'+actionname);
	removeClass(elem,'hidden');
}

function hideAction(actionname,chapterkey){
	var elem = document.getElementById(chapterkey+'-'+actionname);
	addClass(elem,'hidden');
}