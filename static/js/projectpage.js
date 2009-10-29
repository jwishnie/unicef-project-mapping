$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125
    MIN_SCALE = 110735960.625
    WIDTH = 10
    HEIGHT = 17
    
	var map = new OpenLayers.Map( 'map_canvas', {maxScale : MAX_SCALE , minScale : MIN_SCALE });
	var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
	BASE_LAYER, {layers: 'basic'} );
	map.addLayer(layer);
	

	map.setCenter(new OpenLayers.LonLat(longitude, latitude));
	

	var markers = new OpenLayers.Layer.Markers( "Markers" );
	map.addLayer(markers);
				
	var size = new OpenLayers.Size(WIDTH, HEIGHT);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon(imgurl + '/red-marker.png',size,offset);   
	markers.addMarker(new OpenLayers.Marker
					 (new OpenLayers.LonLat(longitude, 
					      latitude),icon.clone()));
	
	addsubprojects(markers);   
}
);
function addsubprojects(markers) {
  for (var i = 0; i < projects.length; i++) {
    subproject = projects[i]; 
	var size = new OpenLayers.Size(WIDTH, HEIGHT);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon(imgurl + '/mini-blue-marker.png',size,offset);   
	markers.addMarker(new OpenLayers.Marker
					 (new OpenLayers.LonLat(subproject['longitude'], 
					      subproject['latitude']),icon.clone()));      
   }
}
