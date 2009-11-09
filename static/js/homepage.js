$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125
    MIN_SCALE = 141700000

    
    $('li.drawer ul:not(:first)').hide();
    $('h3.drawer-handle').click(function() {
        $('li.drawer ul:visible').slideUp().prev().removeClass('open');
        $(this).addClass('open').next().slideDown();
    });

	$("input[type=checkbox]").each(function()
	{
		this.checked = 'yes';
	});


	$('.sectorbox').click(mapEvent);
	$('.implementorbox').click(mapEvent);
	$('[name=Search]').click(searchEvent);
	
	function searchEvent(){
	    var search_url = "/projects/search/" + $('[name=q]').val() + "/";
		$.get(search_url, function(data){
			var projects = eval(data);
			markers.destroy();
			markers = new OpenLayers.Layer.Markers( "Markers" );
			map.addLayer(markers);
			
			var html = "<p>Projects : </p><ol>";
			for(var i = 0;i<projects.length; i++){
			    var project = projects[i];
			    var project_name = project['snippet'].split(":")[0];
			    var project_description = project['snippet'].split(":")[1];			    
			    var project_text = "<div><a href=\"/projects/id/" + project['id'] + "\">" + 
				                        project_name + '</a>' + ' - ' +  project_description + '</div>'
				html += "<li>" + project_text + '</li>';
				var marker_icon = icon.clone()
				marker = new OpenLayers.Marker(
				                new OpenLayers.LonLat(project['longitude'], 
	    						    project['latitude']),marker_icon);
	            marker.events.register("mousedown", {'marker' : marker, 'text' : project_text}, mousedn);
				markers.addMarker(marker);
			}
			html += '</ol>';
			$("#projects").html(html);
			
			$("input[type=checkbox]").each(function()
			{
				this.checked = false;
			});			
            for(var i = 0;i<projects.length; i++){			
			  $("input[type=checkbox]").each(function()
			  {
			      var project = projects[i];
			      if($.inArray(this.value, project['implementors']) > -1) 
			      {
				    this.checked = true;
				  }
			      if($.inArray(this.value, project['sectors']) > -1) 
			      {
				    this.checked = true;
				  }				  
			  });
			}			
		});	  
	}
	
	function constructQueryString(selected_filters){
		var qstring = "";
		for(var i=0; i<selected_filters.length; i++){ qstring += "&" + selected_filters[i].name + "=true"}
		return qstring;
	}
	
	function bookmarkUrl(){
		var queryString = "";
		queryString += constructQueryString($(".sectors input[type=checkbox][checked]"));
		queryString += constructQueryString($(".implementors input[type=checkbox][checked]"));
		var boundingBox = map.getExtent();
		var url = document.location.protocol + "//" + document.location.host + 
				  "/?left=" + boundingBox.left + "&bottom=" + 
				  boundingBox.bottom + "&right=" + boundingBox.right + 
				  "&top=" + boundingBox.top;
		url += queryString;
		$('#bookmark').html(url);
	}

    function mousedn(){
        if(popup != null) {
            popup.destroy();
        }
        popup = new OpenLayers.Popup("project",
                               this.marker.lonlat,
                               new OpenLayers.Size(200,70),
                               this.text,
                               true);        
        map.addPopup(popup);
    }

	function mapEvent(event) {
        var boundingBox = map.getExtent();
		var projects_url = "/projects/bbox/" + boundingBox.left + "/" + 
							boundingBox.bottom + "/" + boundingBox.right + "/" + boundingBox.top + "/";
		var filters = {};
		$(".sectors input[type=checkbox]:checked").each(function(){
			filters[$(this).attr('name')] = true;
		});
		$(".implementors input[type=checkbox]:checked").each(function(){
			filters[$(this).attr('name')] = true;
		});
		
		$.get(projects_url, filters, function(data){
			var projects = eval(data);
			markers.destroy();
			markers = new OpenLayers.Layer.Markers( "Markers" );
			map.addLayer(markers);
			
			var html = "<p>Projects : </p><ol>";
			for(var i = 0;i<projects.length; i++){
			    var project = projects[i];
			    var project_name = project['snippet'].split(":")[0];
			    var project_description = project['snippet'].split(":")[1];			    
			    var project_text = "<div><a href=\"/projects/id/" + project['id'] + "\">" + 
				                        project_name + '</a>' + ' - ' +  project_description + '</div>'
				html += "<li>" + project_text + '</li>';
				var marker_icon = icon.clone()
				marker = new OpenLayers.Marker(
				                new OpenLayers.LonLat(project['longitude'], 
        						    project['latitude']),marker_icon);
                marker.events.register("mousedown", {'marker' : marker, 'text' : project_text}, mousedn);
				markers.addMarker(marker);
			}
			html += '</ol>';
			$("#projects").html(html);
		});
		
		bookmarkUrl();
    }
    var popup = null;
	var bounds= new OpenLayers.Bounds(left, bottom, right, top);

        options = {
            restrictedExtent: bounds, 
            maxScale: MAX_SCALE, 
            minScale: MIN_SCALE,
            eventListeners: { "moveend": mapEvent}
        }

        var map = new OpenLayers.Map( 'map_canvas' , options )
            
	var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS", BASE_LAYER, {layers: 'basic'} );
	map.addLayer(layer);


	map.zoomToExtent(bounds);
	var markers = new OpenLayers.Layer.Markers( "Markers" );
	map.addLayer(markers);
	
	var size = new OpenLayers.Size(10,17);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon('/static/img//mm_20_blue.png',size,offset);
});

function expandOrCollapse(){
    if ($('#left_pane .expand').size() != 0) {
        collapse();
    }
    else {
        expand();
    }
}

function collapse(){
    $('#left_pane span').removeClass("expand");
    $('.expandable_content').hide();
    adjustStylesAfterCollapse();
}

function expand(){
    $('#left_pane span').addClass("expand");
    $('#left_pane span a').html("Hide");
    adjustStylesAfterExpand();
}

function adjustStylesAfterCollapse(){
    $('#left_pane span a').html("Show");
    $('#left_pane').css("width", "0");
    $('#map_canvas').css("width", "974px");
}

function adjustStylesAfterExpand(){
    $('#left_pane').css("width", "170px");
    $('#map_canvas').css("width", "800px");
    $('.expandable_content').show();
}
