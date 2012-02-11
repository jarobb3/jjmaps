function lookup(){
	var q = document.getElementsByName("lookup")[0].value;
	showOverlay();
	downloadUrl('/map', "POST", "q="+q, handleResponse);
	document.getElementsByName("lookup")[0].value = "";
}

function addToRegion(sel){
	var regionkey = sel.options[sel.selectedIndex].value.split(",")[0];
	var statecode = sel.options[sel.selectedIndex].value.split(",")[1];
	
	downloadUrl('/regions/add-state', "POST", "regionkey="+regionkey+"&statecode="+statecode, regionResponse);
	showOverlay();
}

function removeFromRegion(sel){
	statecode = sel.state;
	regionkey = sel.regionkey;
	
	downloadUrl('/regions/remove-state', "POST", "regionkey="+regionkey+"&statecode="+statecode, regionResponse);
	showOverlay();
}

function regionResponse(response){
	var responsejson = eval('(' + response + ')');
	
	var redirecturl = '/chapters?regionkey='+responsejson['regionkey'];
	
	hideOverlay();
	window.location = redirecturl;
}

function showRegion(regionkey){
	//go to the server to get a list of chapternames, chapterkeys
	showOverlay();
	downloadUrl('/map', 'POST', 'regionkey='+regionkey, addRegionsToMap);

	hideAction('display',regionkey);
	showAction('remove',regionkey);
}

function addRegionsToMap(response){
	var responsejson = eval('(' + response + ')');
	illustrate(responsejson, false);
	hideOverlay();
}

function removeRegion(regionkey){
	showOverlay();
	downloadUrl('/regions/get-chapters', 'POST', 'regionkey='+regionkey, removeRegionsFromMap);

	hideAction('remove',regionkey);
	showAction('display',regionkey);
	
	//get a list of chapter keys for the region, call back to removeRegionsFromMap
}

function removeRegionsFromMap(response){
	var responsejson = eval('(' + response + ')');
	chapterkeys = responsejson.chapterkeys;
	
	for( chapterkey in chapterkeys ){
		findAndRemoveShapes(chapterkey);
	}
}

function showChapter(chapterkey){
	//if we've already added the chapter to the map and it's just hidden
	var starti = 0;
	var q = 0;
	
	//find it in the list of chapters displayed
	if( chapterkey in chaptersDisplayed ){
		for( var k in chaptersDisplayed ){
			q = chaptersDisplayed[k]['quantity'];
			if( chapterkey == k ){
				//then reveal the shapes
				var center = revealShapes(starti,starti+q);
				centerMap(center[0],center[1]);
			}
			
			starti += q;
		}
		
		hideAction('display',chapterkey);
		showAction('remove',chapterkey);
		showLegend(chapterkey);
	}
	//if we haven't added the chapter to the map, we need to fetch from database
	else{
		showOverlay();
		
		downloadUrl('/map',"POST","chapterkey="+chapterkey,addChaptersToMap);
	}
}

function findAndRemoveShapes(chapterkey){
	var starti = 0;
	var q = 0;
	for( var k in chaptersDisplayed ){
		q = chaptersDisplayed[k]['quantity'];
		if( chapterkey == k ){
			hideShapes(starti,starti+q);
			break;
		}
		
		starti += q;
	}
}

function removeChapter(chapterkey){
	showOverlay();
	//findAndRemoveshapes(chapterkey);

	var starti = 0;
	var q = 0;
	for( var k in chaptersDisplayed ){
		q = chaptersDisplayed[k]['quantity'];
		if( chapterkey == k ){
			hideShapes(starti,starti+q);
			break;
		}
		
		starti += q;
	}	

	hideAction('remove',chapterkey);
	showAction('display',chapterkey);
	hideLegend(chapterkey);
	
	hideOverlay();
}

function addChaptersToMap(response){
	var responsejson = eval('(' + response + ')');
	
	illustrate(responsejson, true);
	
	hideOverlay();
}

function changeMapTab(tabname){
	if( tabname == 'chapters'){
		showDiv('chapters-list');
		showDiv('show-chapters');
		hideDiv('regions-list');
		hideDiv('show-regions');
	}
	else{
		showDiv('regions-list');
		showDiv('show-regions');
		hideDiv('chapters-list');
		hideDiv('show-chapters');
	}
}

function illustrate(responsejson, onechapter){
	var color;
	var center;
	
	var chaptername;
	var chapterkey;
	var coords;
	
	if(!onechapter) numChaptersAdded++;
	for( var i = 0; i < responsejson['chapterkeys'].length; i++ ){
		if(onechapter) numChaptersAdded++;
		
		chaptername = responsejson['chapternames'][i];
		chapterkey = responsejson['chapterkeys'][i];
		coords = responsejson['coords'][i];
		
		chaptersDisplayed[chapterkey] = { 'quantity' : coords.length }
		
		color = createLegend(chapterkey);
		center = createShape(chaptername,chapterkey,coords,color);
		
		centerMap(center[0],center[1])
		
		hideAction('display',chapterkey);
		showAction('remove',chapterkey);
	}
}

function changeStatus(e){
	alert(e);
}

function createXmlHttpRequest() {
	try {
		if (typeof ActiveXObject != 'undefined') {
			return new ActiveXObject('Microsoft.XMLHTTP');
		} else if (window["XMLHttpRequest"]) {
			return new XMLHttpRequest();
		}
	} catch (e) {
		changeStatus(e);
	}
	return null;
};

function downloadUrl(url, type, data, callback) {
	var status = -1;
	var request = createXmlHttpRequest();
	if (!request) {
		return false;
	}
	request.onreadystatechange = function() {
		if (request.readyState == 4) {
			try {
				status = request.status;
			} catch (e) {
			}
			if (status == 200) {
				callback(request.responseText);
				request.onreadystatechange = function() {};
			}
		}
	}
	
	request.open(type, url, true);
	if (type == "POST") {
		request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		request.setRequestHeader("Content-length", data.length);
		request.setRequestHeader("Connection", "close");
	}
	try {
		request.send(data);
	} catch (e) {
		changeStatus(e);
	}
};

function downloadScript(url) {
	var script = document.createElement('script');
	script.src = url;
	document.body.appendChild(script);
};

