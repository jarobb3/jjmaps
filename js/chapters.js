/*
 * Edit Chapter
 */

function loadChapterToEdit(chapterkey){
	$.ajax({
		url : '/chapters/edit',
		type : 'POST',
		data : {
			'chapterkey' : chapterkey,
		},
		dataType : 'json',
		success : chapterLoaded
	});
}

function chapterLoaded(response){
	var chapter = response.chapter;
	var chapterkey = response.chapterkey;
	
	$('[name="chaptername"]').val(chapter.name);
	$('[name="chapterstate"]').val(chapter.state);
	$('[name="chapterkey"]').val(chapterkey);
	if( chapter.zips.indexOf('Null') == -1 ){
		$('[name="chapterzips"]').val(chapter.zips);
	}
	else{
		$('[name="chapterzips"]').val("");
	}
	if( chapter.counties.indexOf('Null') == -1 ){
		$('[name="chaptercounties"]').val(chapter.counties);
	}
	else{
		$('[name="chaptercounties"]').val("");
	}
	
	$('#update-header').show();
	$('#update-button').show();
	
	$('#create-header').hide();
	$('#create-button').hide();
	
	scrollTo(0,0);
}


/*
 * Change Region tabs on Chapters page
 */

function changeTabsAndGo(tabname){
	var oldselectedtab = $(".selected").removeClass("selected");
	var newselectedtab = $("#"+tabname+"-tab").addClass("selected");
	
	var chapterlists = $(".chapterlist").hide();
	var selectedlist = $("#"+tabname+"chapters-list").show();
}

/*
 * Add a Chapter to a region
 */

function showAddRegionForm(state){
	$("#"+state+"-add-region-form").show();
	$("#"+state+"-add-region-link").hide();
}

function hideAddRegionForm(state){
	$("#"+state+"-add-region-form").hide();
	$("#"+state+"-add-region-link").show();
}

function addToRegion(sel){
	var regionkey = sel.options[sel.selectedIndex].value.split(",")[0];
	var statecode = sel.options[sel.selectedIndex].value.split(",")[1];
	var regionname = sel.options[sel.selectedIndex].innerHTML;
	
	$.ajax({
		url : '/regions/add-state',
		type : 'POST',
		data : {
			'regionkey' : regionkey,
			'statecode' : statecode,
			'regionname' : regionname
		},
		success: regionResponse,
		dataType: 'json'
	});
	showOverlay();
}

function removeFromRegion(statecode){
	$.ajax({
		url : '/regions/remove-state',
		type : 'POST',
		data : {
			'statecode' : statecode
		},
		success : regionResponse,
		dataType : 'json'
	});
	showOverlay();
}

function regionResponse(response){
	window.location.reload();
}