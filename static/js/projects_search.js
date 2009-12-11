$(document).ready(function() {
    $(function() {
    		$("#tabs").tabs();
	});
	
    var is_chrome = (/chrome/).test(navigator.userAgent.toLowerCase());
    if(is_chrome) {
        OpenLayers.DOTS_PER_INCH = 1;
    }

	$("input[type=checkbox]").each(function()
	{
		this.checked = 'yes';
	});

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


	function searchEvent(){
        var text = escape($('[name=q]').val());
        if($.trim(text)) {
	    var search_url = "/projects/search/";
		$.get(search_url);	  
        }
        
        bookmarkUrl();
	}

    function removeAllSectorsAndImplementors() {
        $("input[type=checkbox]").each(function() {
                this.checked = false;
        });			
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

	$('[name=Search]').click(searchEvent);
    $('#search').focus();
    
    $('#kml-id').bind('click', switchKMLView);

    function switchKMLView(){
        var layers;
        $.get("/kml_layers/", function(data){
            layers = eval(data);
            if(layers.length >0){
               add_kml_info(layers);
            }else{
                $('#kml').html('No KML layers to overlay');
            }

        });

    }


    function add_kml_info(layers){
        var kml_html = "<ul>";
        for(var i=0; i < layers.length; i++){
            var layer = layers[i];
            kml_html += "<li>";
            kml_html += "<input type='checkbox' id='kml_" + layer.id + "'></input>";
            kml_html += "<span>" + layer.name + "</span>";
            kml_html += "</li>";
        }
        kml_html += "</ul>";
        $('#kml').html(kml_html);
    }
    	
});