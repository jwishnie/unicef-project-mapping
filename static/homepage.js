$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125
    MIN_SCALE = 110735960.625
    
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



	function mapEvent(event) {
        var boundingBox = map.getExtent();
		var projects_url = "/projects/bbox/" + boundingBox.left + "/" + 
							boundingBox.bottom + "/" + boundingBox.right + "/" + boundingBox.top + "/";
		var filters = {};
		$(".sectors input[type=checkbox][checked]").each(function(){
			filters[$(this).attr('name')] = true;
		});
		$(".implementors input[type=checkbox][checked]").each(function(){
			filters[$(this).attr('name')] = true;
		});
		
		$.get(projects_url, filters, function(data){
			var projects = eval(data);
			markers.destroy();
			markers = new OpenLayers.Layer.Markers( "Markers" );
			map.addLayer(markers);
			
			var html = "<p>Projects : </p><ol>";
			for(var i=0; i<projects.length; i++){
				html += "<li><div>" + projects[i]['snippet'] + '</div></li>';
				markers.addMarker(new OpenLayers.Marker
								 (new OpenLayers.LonLat(projects[i]['longitude'], 
								      projects[i]['latitude']),icon.clone()));
			}
			html += '</ol>';
			$("#projects").html(html);
		});
		
		bookmarkUrl();
    }

	var map = new OpenLayers.Map( 'map_canvas' , 
				  {eventListeners: {"moveend": mapEvent}, maxScale : MAX_SCALE , minScale : MIN_SCALE });
	var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
	BASE_LAYER, {layers: 'basic'} );
	map.addLayer(layer);

	var bounds= new OpenLayers.Bounds(left, bottom, right, top);
	map.zoomToExtent(bounds);
	var markers = new OpenLayers.Layer.Markers( "Markers" );
	map.addLayer(markers);
				
	var size = new OpenLayers.Size(10,17);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon('http://labs.google.com/ridefinder/images/mm_20_blue.png',size,offset);
});