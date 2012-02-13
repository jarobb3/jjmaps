function GetMap() {
	map = new Microsoft.Maps.Map(
			document.getElementById('mapDiv'),
			{
				credentials: 'Aowawt5472nQChYkKj-iqY5Uvr600kMLZ_I2xPttJ_7bot3OVPc0ltzDM2RIxQKU',
				center: new Microsoft.Maps.Location(43.06888777, -106.171875),
				zoom: 3,
				enableSearchLogo: false,
				enableClickableLogo: false,
				showScalebar: false,
				showBreadcrumb: true,
				showMapTypeSelector:false
			});
}

function createShape(chaptername, chapterkey, coords, color){
	var starti = map.entities.getLength();
	var options = {
			fillColor: new Microsoft.Maps.Color(parseInt(color[0]),parseInt(color[1]),parseInt(color[2]),parseInt(color[3])),
			strokeColor: new Microsoft.Maps.Color(100,255,255,255),
			strokeThickness: parseInt(1),
			
	};
	
	for( var i = 0; i < coords.length; i++ ){
		locationobjlist = [];
		for( var j = 0; j < coords[i].length; j++ ){
			c = prepCoord(coords[i][j]);
			locationobjlist.push(new Microsoft.Maps.Location(c[1], c[0]));
		}
		polygon = new Microsoft.Maps.Polygon(locationobjlist,options);
		map.entities.push(polygon);
	}
	
	var endi = map.entities.getLength();
	
	return { 'center' : [c[1],c[0]], 'start' : starti, 'end' : endi };
}

function centerMap(xcoord,ycoord){
	map.setView({animate: false, zoom:6, center: new Microsoft.Maps.Location(xcoord,ycoord)});
}

function revealShapes(startIndex,endIndex){
	var polygon;
	for( var i=endIndex-1; i>=startIndex; i--){
		polygon = map.entities.get(i);
		polygon.setOptions({visible: true});
	}
	var locs = polygon.getLocations();
	return [locs[locs.length-1].latitude,locs[locs.length-1].longitude];
}

function hideShapes(startIndex,endIndex){
	for( var i=endIndex-1; i>=startIndex; i-- ) {
		//map.entities.removeAt(i);
		var polygon = map.entities.get(i);
		polygon.setOptions({visible: false}); 
	}
}

function prepCoord(coord){
	return coord.trim().replace(/\s/,",").replace(/\s/g,"").split(",");
}