$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125;
    MIN_SCALE = 141700000;
    // pink tile avoidance
    OpenLayers.IMAGE_RELOAD_ATTEMPTS = 5;
    // make OL compute scale according to WMS spec
    OpenLayers.DOTS_PER_INCH = 25.4 / 0.28;

    $('ul.sectors').hide();
    $('ul.implementors').hide();
    
    $('span#sector').click(function() {
        if ($('li.implementor_drawer span.open').size() != 0) {
            collapseImplementors();
        }
        if ($('li.sector_drawer span.open').size() != 0) {
            collapseSectors();
        }
        else {
            expandSectors();
        }
    });
    
    $('span#implementor').click(function() {
        if ($('li.sector_drawer span.open').size() != 0) {
            collapseSectors();
        }
        if ($('li.implementor_drawer span.open').size() != 0) {
            collapseImplementors();
        }         
        else {
            expandImplementors();
        }
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
			var projects = JSON.parse(data.replace(/'/g, '"'));
			markers.destroy();
			markers = new OpenLayers.Layer.Markers( "Markers" );
			map.addLayer(markers);
			
			var html = "<h4 class=\"top_round_corner\">List of Projects: </h4><ol>";
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
            bookmarkUrl();
	}
	
	function constructQueryString(selected_filters){
		var qstring = "";
		for(var i=0; i<selected_filters.length; i++){ qstring += "&" + selected_filters[i].name + "=true"}
		return qstring;
	}
	
	function bookmarkUrl(){
		var queryString = "";
		queryString += constructQueryString($(".sectors input[type=checkbox]:checked"));
		queryString += constructQueryString($(".implementors input[type=checkbox]:checked"));
		var boundingBox = map.getExtent();
		var url = document.location.protocol + "//" + document.location.host + 
				  "/?left=" + boundingBox.left + "&bottom=" + 
				  boundingBox.bottom + "&right=" + boundingBox.right + 
				  "&top=" + boundingBox.top +
                                  "&tag=" + search_tag +
                                  "&search_term=" + $("#search").val();
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
		
		filters["tag"] = search_tag;
                filters["search_term"] = $("#search").val();
		
		$.get(projects_url, filters, function(data){
			var projects = JSON.parse(data.replace(/'/g, '"'));

			markers.destroy();
			markers = new OpenLayers.Layer.Markers( "Markers" );
			map.addLayer(markers);
			
			var html = "<h4 class=\"top_round_corner\">List of Projects: </h4><ol>";
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
            restrictedExtent: new OpenLayers.Bounds(-180,-90, 180, 90), 
            maxScale: MAX_SCALE, 
            minScale: MIN_SCALE,
            eventListeners: { "moveend": mapEvent}
        }

        var map = new OpenLayers.Map( 'map_canvas' , options );
            
        var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS", BASE_LAYER, {layers: 'basic'} );
        map.addLayer(layer);
        
        var gs = "http://"+ window.location.host+"/geoserver/ows";
        
        var dists = new OpenLayers.Layer.WMS(
                   "Dists",
                   gs,
                   { 
                       layers: 'GADM:UGA_adm1',
                       transparent: true,
                       format: 'image/png',
                   },
                   {
                       isBaseLayer: false
                   }
        );
        
        dists.setOpacity(0.5);
        map.addLayer(dists);
                                             
        

	map.zoomToExtent(bounds);
	var markers = new OpenLayers.Layer.Markers( "Markers" );
	map.addLayer(markers);
	
	var size = new OpenLayers.Size(10,17);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon('/static/img//mm_20_blue.png',size,offset);
});

function collapseSectors(){
    $('ul.sectors').hide();
    $('li.sector_drawer div').css("background-color", "#A5A5A5");
    $('li.sector_drawer span').removeClass('open');   
}

function expandSectors(){
    $('ul.sectors').show();
    $('li.sector_drawer div').css("background-color", "#054862");            
    $('ul.sectors').css("background-color", "#054862");            
    $('li.sector_drawer span').addClass('open');   
}

function collapseImplementors(){
    $('ul.implementors').hide();
    $('li.implementor_drawer div').css("background-color", "#A5A5A5");
    $('li.implementor_drawer span').removeClass('open');   
}

function adjustStylesAfterExpand(){
    $('#left_pane').css("width", "170px");
    $('#map_canvas').css("width", "800px");
    $('.expandable_content').show();
}

$(document).ready(function(){ 
  $('input[type=text]').focus(function(){ 
    if($(this).val() == $(this).attr('defaultValue'))
    {
      $(this).val('');
    }
  });
  
  $('input[type=text]').blur(function(){
    if($(this).val() == '')
    {
      $(this).val($(this).attr('defaultValue'));
    } 
  });
}); 

function expandImplementors(){
    $('ul.implementors').show();
    $('li.implementor_drawer div').css("background-color", "#054862");
    $('ul.implementors').css("background-color", "#054862");
    $('li.implementor_drawer span').addClass('open');   
}
