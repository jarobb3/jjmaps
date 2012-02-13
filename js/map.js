/*
 * Visual helpers
 */

function toggleObjectActions(chapterkey){
	$('#'+chapterkey+'-'+'display').toggleClass('hidden');
	$('#'+chapterkey+'-'+'remove').toggleClass('hidden');
}

/*
 * Add / Remove Chapters
 */

function fetchChapter( chapterkey ){
	$.ajax({
		url : '/map',
		type : 'POST',
		data : {
			'chapterkey' : chapterkey,
		},
		success : addChapters,
		dataType : 'json'
	});
	showOverlay();
}

function showChapter(chapterkey){
/*
 * If the chapter is local memory
 */
	try{
		var shapeinfo = chaptersDisplayed[chapterkey];
		var center = revealShapes( shapeinfo.start, shapeinfo.end );
		centerMap(center[0], center[1]);
		
		toggleObjectActions(chapterkey);
		showLegend(chapterkey);
	}
/*
 * ReferenceError, therefore it's not. We have to fetch the chapter from the server.
 */
	catch(err){
		fetchChapter(chapterkey);
	}
}

function removeChapter(chapterkey){
	showOverlay();
	
	var shapeinfo = chaptersDisplayed[chapterkey];
	hideShapes( shapeinfo.start, shapeinfo.end );
	
	toggleObjectActions(chapterkey);
	hideLegend(chapterkey);
	
	hideOverlay();	
}

/*
 * Toggle Tabs : Chapters / Regions
 */
function changeMapTab(tabname){
	//show / hide lists
	$('.selectionlist').hide();
	$('#'+tabname+'-list').show();
	$('#show'+tabname).show();
	
	//change selected tab
	var oldselectedtab = $(".selected").removeClass("selected");
	var newselectedtab = $("#"+tabname+"-tab").addClass("selected");
}

/*
 * Search for a Zip
 */

function lookupZip(){
	var queryElem = $('[name="lookup"]');
	var q = queryElem.val();
	queryElem.val("");
	
	if( q != ""){
		$.ajax({
			url : '/map/search',
			type : 'POST',
			data : { 'q' : q },
			success : addChapters,
			dataType : 'json'
		});
		
		showOverlay();
	}
}

/*
 * Response Handler for adding chapters to the map
 */

function addChapters(response){
	var chapters = response.chapters;
	
	var color;
	var shapeinfo;
	for( var i = 0; i < chapters.length; i++ ){
		chapter = chapters[i];
		
		color = createLegend(chapter.key);
		shapeinfo = createShape(chapter.name, chapter.key, chapter.coords, color);
		
		centerMap( shapeinfo.center[0], shapeinfo.center[1] );
		chaptersDisplayed[chapter.key] = { 'start' : shapeinfo.start, 'end' : shapeinfo.end };
		
		toggleObjectActions(chapter.key);
	}
	
	hideOverlay();
}

/*
 * Add / Remove Regions
 */

function fetchRegion(regionkey){
	$.ajax({
		url : '/regions/show',
		type : 'POST',
		data : {
			'regionkey' : regionkey,
		},
		success : addRegion,
		dataType : 'json'
	});
	showOverlay();
}

function showRegion(regionkey){
/*
 * If the region is local memory
 */
	try{
		var shapeinfo = chaptersDisplayed[regionkey];
		var center = revealShapes( shapeinfo.start, shapeinfo.end );
		centerMap(center[0], center[1]);
		
		toggleObjectActions(regionkey);
		showLegend(regionkey);
	}
/*
 * ReferenceError, therefore it's not. We have to fetch the region from the server.
 */
	catch(err){
		fetchRegion(regionkey);
	}
	
}

function addRegion(response){
	var chapters = response.chapters;
	var regionkey = response.regionkey;
	
	var shapeinfo;
	var start;
	var end;
	
	var color = createLegend(regionkey);
	for( var i = 0; i < chapters.length; i++ ){
		chapter = chapters[i];
		
		shapeinfo = createShape(chapter.name, chapter.key, chapter.coords, color);
		if( i == 0 ) start = shapeinfo.start;
		else if( i == chapters.length-1 ) end = shapeinfo.end;
		else{}
		
	}

	toggleObjectActions(regionkey);

	centerMap( shapeinfo.center[0], shapeinfo.center[1] );
	chaptersDisplayed[regionkey] = { 'start' : start, 'end' : end };
	
	hideOverlay();	
}

function removeRegion(regionkey){
	showOverlay();
	
	var shapeinfo = chaptersDisplayed[regionkey];
	hideShapes( shapeinfo.start, shapeinfo.end );
	
	toggleObjectActions(regionkey);
	hideLegend(regionkey);
	
	hideOverlay();	
}