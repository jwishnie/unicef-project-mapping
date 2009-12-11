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

    var active_kml_layers;
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
        var layersInMap = map.layers;
        var layerToQuery = "";
        $.each(layersInMap, function(){
            if(! this.isBaseLayer){
                if(this.visibility){
                    layerToQuery = this.params.LAYERS;
                }
            }
        });
		$("#stats").html("Loading. Please wait...");
		                    var params = {
		                        REQUEST: "GetFeatureInfo",
		                        EXCEPTIONS: "application/vnd.ogc.se_xml",
		                        BBOX: map.getExtent().toBBOX(),
		                        X: e.xy.x,
		                        Y: e.xy.y,
		                        INFO_FORMAT: 'text/plain',
		                        QUERY_LAYERS: layerToQuery,
		                        FEATURE_COUNT: 50,
		                        Layers: layerToQuery,
		                        Styles: '',
		                        Srs: 'EPSG:4326',
		                        WIDTH: map.size.w,
		                        HEIGHT: map.size.h,
		                        format: format};
		                    OpenLayers.loadURL("http://"+window.location.host+"/geoserver/wms", params, this, populateRegionStats, populateRegionStats);
		                    OpenLayers.Event.stop(e);
        }
        var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS", BASE_LAYER, {layers: 'basic'},{'displayInLayerSwitcher':false} );
        map.addLayer(layer);

        
        var gs = "http://"+window.location.host+"/geoserver/ows";
        var countryLayer = new OpenLayers.Layer.WMS(
            "Uganda",
            gs,
            { 
               layers: 'GADM:UGA_adm0',
               transparent: true,
               format: 'image/png'
            },
            {
               isBaseLayer: false,
               visibility: true
            }
        );

        countryLayer.setOpacity(0.5);

        var dists = new OpenLayers.Layer.WMS(
                   "Districts",
                   gs,
                   { 
                       layers: 'GADM:UGA_adm1',
                       transparent: true,
                       format: 'image/png'
                   },
                   {
                       isBaseLayer: false,
                       visibility: false
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
                   isBaseLayer: false,
                   visibility: false
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
    $('#kml-id').bind('click', switchKMLView);

    function switchKMLView(){
        remove_all_layers();
        var layers;
        $.get("/kml_layers/", function(data){
            layers = eval(data);
            if(layers.length >0){
               add_kml_info(layers);
            }else{
                $('#kml').html('No KML layers to overlay');
            }
            
        });
        $('#stats-id').bind('click', switchStatsView);
        $('#proj-id').bind('click', projectview);
        
    }
    
    function switchStatsView(){
        $("#filterable_criteria").hide();
        $("#layercontrols").show();
        remove_all_layers();
        map.addLayer(countryLayer);
        map.addLayer(dists);
        map.addLayer(county);
        var layersInMap = map.layers;
        $("#layerholder").html("");
        $.each(layersInMap, function(){
            if(! this.isBaseLayer){
                var isChecked = "";
                if(this.visibility) {
                    isChecked = 'checked="checked"';
                }
                var htmlLayer = '<li><input type="radio" name="layergroup" value="'+this.name+'" class="radiolayer"'+isChecked+'" /><label>'+this.name+'</label></li><p/>';
                $("#layerholder").append(htmlLayer);
                $(".radiolayer").bind('click', switchLayer);
            }
        });
        $('#stats-id').unbind('click', switchStatsView);
        $('#proj-id').bind('click', projectview);
        map.events.register('click', map, queryForRegionData);
        map.events.unregister('moveend', map, mapEvent);
    }
        
    function projectview(){
        $("#filterable_criteria").show();
        $("#layercontrols").hide();
        remove_all_layers();
        map.addLayer(markers);
        $('#stats-id').bind('click', switchStatsView);
        $('#proj-id').unbind('click', projectview);
        map.events.register('moveend', map, mapEvent);
        map.events.unregister('click', map, queryForRegionData);
    }
    
    function switchLayer(event){
        var layerName = $(this).attr("value");
        var layersInMap = map.layers;
        $.each(layersInMap, function(){
            if(!this.isBaseLayer){
                if(this.name === layerName){
                    this.setVisibility(true);
                }else{
                    this.setVisibility(false);
                }
            }
        });
    }
        
    function add_kml_info(layers){
        var kml_html = "<ul>";
        for(var i=0; i < layers.length; i++){
            var layer = layers[i];
            kml_html += "<li>";
            kml_html += "<input type='checkbox' class='kml_checkbox' id='kml_" + layer.kml_id + "'></input>";
            kml_html += "<span>" + layer.name + "</span>";
            kml_html += '<span class="kml_file" id="file_kml_' + layer.kml_id + '">' + layer.file + "</span>";
            kml_html += "</li>";
            
        }
        kml_html += "</ul>";
        $('#kml').html(kml_html);
        $(".kml_checkbox").click(show_hide_kml_layers);
    }
    
    function show_hide_kml_layers(){
        if(this.checked == false){
            layer = map.getLayersByName(this.id)[0];
            map.removeLayer(layer);
        }else{
            kml_file = $("#file_" + this.id).html();
            map.addLayer(new OpenLayers.Layer.GML(this.id, kml_file, 
               {
                format: OpenLayers.Format.KML, 
                formatOptions: {
                  extractStyles: true, 
                  extractAttributes: true,
                  maxDepth: 2
                }
               }));
        }
    }
    
    function remove_all_layers(){
        var layersInMap = map.layers;
        $.each(layersInMap, function(){
            if(!this.isBaseLayer){
                map.removeLayer(this);
            }
        });
        
        
        layersInMap = map.layers;
        $.each(layersInMap, function(){
            alert(this.name);
        });
    }
    
    
});
