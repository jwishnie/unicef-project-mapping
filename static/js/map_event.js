$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125;
    MIN_SCALE = 100000000;

    // pink tile avoidance
    OpenLayers.IMAGE_RELOAD_ATTEMPTS = 5;
    // make OL compute scale according to WMS spec
    OpenLayers.DOTS_PER_INCH = 25.4 / 0.28;
    
    function constructQueryString(selected_filters){
    	var qstring = "";
    	for(var i=0; i<selected_filters.length; i++){ qstring += "&" + selected_filters[i].name + "=true";}
    	return qstring;
    }
    
	var size = new OpenLayers.Size(10,17);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon('/static/img//bright_red_marker.png',size,offset);
    var popup = null;
    	
	function mousedn() {
        if(popup !== null) {
            popup.destroy();
        }
        popup = new OpenLayers.Popup("project",
                               this.marker.lonlat,
                               new OpenLayers.Size(200,70),
                               this.text,
                               true);        
        map.addPopup(popup);
    }
    	
	function addProjectsOnMap(projects) {
        markers.destroy();
        markers = new OpenLayers.Layer.Markers( "Markers" );
        map.addLayer(markers);
        var html = "<ul>";
        if(projects.length == 0) {
            $("#search_page h3").hide();
            $("#map_canvas").hide();
            $("#projects").hide();
            $("#projects_searched").hide();

            var html_text = "<h3>Sorry. No results found for <span class='search_term'>\"" + search_term + "\"</span>:</h3>";
            $("#search_page").html(html_text);
        }
        
        for(var i = 0;i<projects.length; i++){
            var project = projects[i];
            var project_name = project.snippet.split(":")[0];
            var project_description = project.snippet.split(":")[1];			    
            var project_text = "<a href=\"/projects/id/" + project.id + "/" +"\">" + 
                                        project_name + '</a><div class="proj_desc">' +  project_description + '</div>';
            html += "<li>" + project_text + "</li>";
            var marker_icon = icon.clone();
            marker = new OpenLayers.Marker(
                                new OpenLayers.LonLat(project.longitude, 
                                            project.latitude),marker_icon);
            marker.events.register("mousedown", {'marker' : marker, 'text' : project_text}, mousedn);
            markers.addMarker(marker);
        }
        html += "</ul>";
        $("#proj").html(html);
    }
    
    function mapEvent(event) {
        var boundingBox = map.getExtent();
		var projects_url = "/projects/bbox/" + boundingBox.left + "/" + 
							boundingBox.bottom + "/" + boundingBox.right + "/" + boundingBox.top + "/";
		var filters = {};

		filters.tag = search_tag;

		$.get(projects_url, filters, function(data) {
            addProjectsOnMap(projects);
		});
    }
    
    var options = {
        maxScale: MAX_SCALE, 
        minScale: MIN_SCALE
    };
    
    var map = new OpenLayers.Map( 'map_canvas' , options );
    
    var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS", BASE_LAYER, {layers: 'basic'},{'displayInLayerSwitcher':false} );
    var markers = new OpenLayers.Layer.Markers( "Markers" );
    var bounds= new OpenLayers.Bounds(left, bottom, right, top);    
    
    map.events.register('moveend', map, mapEvent);
    map.addLayer(layer);
    map.zoomToExtent(bounds);
	map.addLayer(markers);
});