function showChapter(chapterkey){
	//if we've already added the chapter to the map and it's just hidden
	var starti = 0;
	var q = 0;
	if( chapterkey in chaptersDisplayed ){
		for( var k in chaptersDisplayed ){
			q = chaptersDisplayed[k]['quantity'];
			if( chapterkey == k){
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
		
		hideAction('display',chapterkey);
		showAction('remove',chapterkey);
		
		numChaptersAdded++;
		
		downloadUrl('/map',"POST","chapterkey="+chapterkey,handleResponse);
	}
}

function removeChapter(chapterkey){
	showOverlay();

	var starti = 0;
	var q = 0;
	for( var k in chaptersDisplayed ){
		q = chaptersDisplayed[k]['quantity'];
		if( chapterkey == k ){
			hideShapes(starti,starti+q);
			//delete chaptersDisplayed[k];
			break;
		}
		
		starti += q;
	}	

	hideAction('remove',chapterkey);
	showAction('display',chapterkey);
	hideLegend(chapterkey);
	
	hideOverlay();
}

function handleResponse(response){
	var responsejson = eval('(' + response + ')');
	
	var chaptername = responsejson['chaptername'];
	var chapterkey = responsejson['chapterkey'];
	var coords = responsejson['coords'];
	
	chaptersDisplayed[chapterkey] = {'quantity' : coords.length };
	
	var color = createLegend(chapterkey);
	var center = createShape(chaptername,chapterkey,coords,color);
	centerMap(center[0],center[1]);
	
	hideOverlay();
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
}