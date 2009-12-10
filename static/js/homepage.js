function collapseSectors(){
    $('ul.sectors').hide();
    $('li.sector_drawer div').css("background-color", "#007BD6");
    $('li.sector_drawer span').removeClass('open');   
}

function expandSectors(){
    $('ul.sectors').show();
    $('li.sector_drawer div').css("background-color", "#007BD6");
    $('ul.sectors').css("background-color", "#FFF");            
    $('ul.sectors').css("color", "#000");            
    $('li.sector_drawer span').addClass('open');   
}

function collapseImplementors(){
    $('ul.implementors').hide();
    $('li.implementor_drawer div').css("background-color", "#007BD6");
    $('li.implementor_drawer span').removeClass('open');   
}

function adjustStylesAfterExpand(){
    $('#left_pane').css("width", "170px");
    $('#map_canvas').css("width", "800px");
    $('.expandable_content').show();
}

function expandImplementors(){
    $('ul.implementors').show();
    $('li.implementor_drawer div').css("background-color", "#007BD6");
    $('ul.implementors').css("background-color", "#FFF");
    $('ul.implementors').css("color", "#000");
    $('li.implementor_drawer span').addClass('open');   
}

function populateRegionStats(response){
	$.post("/search_admin_unit/",{text:response.responseText},
	    function(data){
	        $("#stats").html(data);
	    });
}

$(document).ready(function() {
    $(function() {
    		$("#tabs").tabs();
    	});
    	
    
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125;
    MIN_SCALE = 200000000;

    // pink tile avoidance
    OpenLayers.IMAGE_RELOAD_ATTEMPTS = 5;
    // make OL compute scale according to WMS spec
    OpenLayers.DOTS_PER_INCH = 25.4 / 0.28;

    var is_chrome = (/chrome/).test(navigator.userAgent.toLowerCase());
    if(is_chrome) {
        OpenLayers.DOTS_PER_INCH = 1;
    }

    $('#filterable_criteria ul.sectors').hide();
    $('#filterable_criteria ul.implementors').hide();
    
    $('#filterable_criteria li.sector_drawer div').click(function() {
        if ($('#filterable_criteria li.implementor_drawer span.open').size() !== 0) {
            collapseImplementors();
        }
        if ($('#filterable_criteria li.sector_drawer span.open').size() !== 0) {
            collapseSectors();
        }
        else {
            expandSectors();
        }
    });
    
    $('#filterable_criteria li.implementor_drawer div').click(function() {
        if ($('#filterable_criteria li.sector_drawer span.open').size() !== 0) {
            collapseSectors();
        }
        if ($('#filterable_criteria li.implementor_drawer span.open').size() !== 0) {
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


	function searchEvent(){
        var text = escape($('[name=q]').val());
        if($.trim(text)) {
	    var search_url = "/projects/search/" + escape($('[name=q]').val()) + "/";
		$.get(search_url, function(data){
                  var projects = getProjects(data);
                  addProjectsOnMap(projects);	
                  removeAllSectorsAndImplementors();
                  selectOnlySectorsAndImplementorsForProjects(projects);
        });	  

        bookmarkUrl();
        }
	}

        function removeAllSectorsAndImplementors() {
            $("input[type=checkbox]").each(function() {
                    this.checked = false;
            });			
        }

        function getProjects(data) {
            return JSON.parse(data);
        }

        function selectOnlySectorsAndImplementorsForProjects(projects) {
            for(var i = 0;i<projects.length; i++) {
			  $("input[type=checkbox]").each(function()
			  {
			      var project = projects[i];
			      if($.inArray(this.value, project.implementors) > -1) {
				    this.checked = true;
			       }
			      if($.inArray(this.value, project.sectors) > -1) {
				    this.checked = true;
			      }				  
			  });
			}			
        }
	
	function constructQueryString(selected_filters){
		var qstring = "";
		for(var i=0; i<selected_filters.length; i++){ qstring += "&" + selected_filters[i].name + "=true";}
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
		
		filters.tag = search_tag;
                filters.search_term = escape($("#search").val());
		
		$.get(projects_url, filters, function(data) {
                var projects = getProjects(data);
                addProjectsOnMap(projects);
		});
		
		bookmarkUrl();
    }


    function addProjectsOnMap(projects) {
        markers.destroy();
        markers = new OpenLayers.Layer.Markers( "Markers" );
        map.addLayer(markers);
        var html = "<ul>";
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

        var popup = null;
	var bounds= new OpenLayers.Bounds(left, bottom, right, top);

        options = {
            maxScale: MAX_SCALE, 
            minScale: MIN_SCALE
            //eventListeners: { "moveend": mapEvent}
        };

		
		format = 'image/png';
        var map = new OpenLayers.Map( 'map_canvas' , options );
         map.events.register('moveend', map, mapEvent);
        
 
      function queryForRegionData(e){
			$("#stats").html("Loading. Please wait...");
			                    var params = {
			                        REQUEST: "GetFeatureInfo",
			                        EXCEPTIONS: "application/vnd.ogc.se_xml",
			                        BBOX: map.getExtent().toBBOX(),
			                        X: e.xy.x,
			                        Y: e.xy.y,
			                        INFO_FORMAT: 'text/plain',
			                        QUERY_LAYERS: 'GADM:UGA_adm1',
			                        FEATURE_COUNT: 50,
			                        Layers: 'GADM:UGA_adm1',
			                        Styles: '',
			                        Srs: 'EPSG:4326',
			                        WIDTH: map.size.w,
			                        HEIGHT: map.size.h,
			                        format: format};
			                    OpenLayers.loadURL("http://"+window.location.host+"/geoserver/wms", params, this, populateRegionStats, populateRegionStats);
			                    OpenLayers.Event.stop(e);
			
}
        var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS", BASE_LAYER, {layers: 'basic'},{'displayInLayerSwitcher':false} );
        // var layer = new OpenLayers.Layer.VirtualEarth("Hybrid", {
        //     type: VEMapStyle.Aerial
        // });
        
        map.addLayer(layer);
        
        // map.addLayer(new OpenLayers.Layer.GML("KML", "/static/fertility_world_polygon.kml", 
        //    {
        //     format: OpenLayers.Format.KML, 
        //     formatOptions: {
        //       extractStyles: true, 
        //       extractAttributes: true,
        //       maxDepth: 2
        //     }
        //    }));
        
        var gs = "http://"+window.location.host+"/geoserver/ows";
        var dists = new OpenLayers.Layer.WMS(
                   "Districts",
                   gs,
                   { 
                       layers: 'GADM:UGA_adm1',
                       transparent: true,
                       format: 'image/png'
                   },
                   {
                       isBaseLayer: false
                   }
        );
        
        dists.setOpacity(0.5);
                                             
         var county = new OpenLayers.Layer.WMS(
               "County",
               gs,
               { 
                   layers: 'GADM:UGA_adm2',
                   transparent: true,
                   format: 'image/png'
               },
               {
                   isBaseLayer: false
               }
           );

    county.setOpacity(0.5);

	map.zoomToExtent(bounds);
	var markers = new OpenLayers.Layer.Markers( "Markers" );
	map.addLayer(markers);
	
	var size = new OpenLayers.Size(10,17);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon('/static/img//bright_red_marker.png',size,offset);
	$('.sectorbox').click(mapEvent);
	$('.implementorbox').click(mapEvent);
	$('[name=Search]').click(searchEvent);
        $('#search').focus();
        $("#search").keyup(function (e) {
        if (e.which == 32 || e.which == 8 || (47 <= e.which && e.which <= 47 + 10) 
                          ||(65 <= e.which && e.which <= 65 + 25)
                          || (97 <= e.which && e.which <= 97 + 25)) {
            if (e.which == 8 && !($.trim(escape($('[name=q]').val())))) {
              mapEvent($.Event("MapEvent"));              
            } else {
              searchEvent();
            }

          }
        });
        
    $('#stats-id').bind('click', switchStatsView);
    
    function switchStatsView(){
        map.addControl(new OpenLayers.Control.LayerSwitcher());
        map.addLayer(dists);
        map.addLayer(county);
        map.removeLayer(markers);
        $('#stats-id').unbind('click', switchStatsView);
        $('#proj-id').bind('click', projectview);
        map.events.register('click', map, queryForRegionData);
        map.events.unregister('moveend', map, mapEvent);
    }
        
    function projectview(){
        var switcher = map.getControlsByClass("OpenLayers.Control.LayerSwitcher");
        if(switcher.length > 0){
            jQuery.each(switcher, function(l){
                map.removeControl(l);
            });
        }
        map.removeLayer(dists);
        map.removeLayer(county);
        map.addLayer(markers);
        $('#stats-id').bind('click', switchStatsView);
        $('#proj-id').unbind('click', projectview);
        map.events.register('moveend', map, mapEvent);
        map.events.unregister('click', map, queryForRegionData);
    }
    
});
