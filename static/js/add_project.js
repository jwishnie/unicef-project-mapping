jQuery(document).ready(function(){
    var map;
    var markers;
    
    OpenLayers.Control.Click = 
        OpenLayers.Class(OpenLayers.Control, {                
            defaultHandlerOptions: {
                'single': true,
                'double': false,
                'pixelTolerance': 0,
                'stopSingle': false,
                'stopDouble': false
            },
        
            initialize: function(options) {
                this.handlerOptions = OpenLayers.Util.extend(
                    {}, this.defaultHandlerOptions
                );
                OpenLayers.Control.prototype.initialize.apply(
                    this, arguments
                ); 
                this.handler = new OpenLayers.Handler.Click(
                    this, {
                        'click': this.trigger
                    }, this.handlerOptions
                );
            }, 
        
            trigger: function(e) {
                var lonlat = map.getLonLatFromViewPortPx(e.xy);
                markers.destroy();
                markers = new OpenLayers.Layer.Markers( "Markers" );
                map.addLayer(markers);
                var marker_icon = icon.clone();
                marker = new OpenLayers.Marker(
                                    new OpenLayers.LonLat(lonlat.lon, 
                                                lonlat.lat),marker_icon);
                // marker.events.register("mousedown", {'marker' : marker, 'text' : project_text}, mousedn);
                markers.addMarker(marker);
                jQuery("#id_latitude")[0].value = lonlat.lat;
                jQuery("#id_longitude")[0].value = lonlat.lon;
            }
        });
    
    
    map = new OpenLayers.Map('map');
    
    markers = new OpenLayers.Layer.Markers( "Markers" );
	map.addLayer(markers);
	var size = new OpenLayers.Size(10,17);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon('/static/img//mm_20_blue.png',size,offset);
    
    var ol_wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
        "http://labs.metacarta.com/wms/vmap0",
        {layers: 'basic'} );
    map.addLayer(ol_wms);
    if (!map.getCenter()) map.zoomToMaxExtent();
    var click = new OpenLayers.Control.Click();
    map.addControl(click);
    click.activate();
    
    plot_project();
    
    

	var sector_names = sectors.split(", ");
	jQuery("#id_project_sectors").autocomplete(sector_names, {
		multiple: true,
		autoFill: true
	});
	
	var implementor_names = implementors.split(", ");
	jQuery("#id_project_implementors").autocomplete(implementor_names, {
		multiple: true, 
		autoFill: true
	});
	
	var sector_list = sectors.split(", ").splice(0,5).join(", ");
	var implementor_list = implementors.split(", ").splice(0,5).join(", ");
	jQuery("#sector_examples").html(sector_list);
	jQuery("#implementor_examples").html(implementor_list);

    function add_video(){
        var video_url_count = jQuery(".add_video_url").length;
    	if(video_url_count==1){
            jQuery("#video_url_1").append('<input type="radio" name="default_video" value="video_1"></input>');
            jQuery("#video_url_1").append('<span class="remove_video" id="remove_video_' + video_id + '">remove</span>');
        }
        video_id += 1;
        var div_element = '<div id="video_url_' + video_id + '" class="add_video_url">';
        div_element +=  '<label>Video URL : </label>';
        div_element +=  '<input type="text" name="video_url_' + video_id + '"></input>';
        div_element +=  '<input type="radio" name="default_video" value="video_'+ video_id + '"></input>';
        div_element +=  '<span class="remove_video" id="remove_video_' + video_id +'">remove</span>';
        div_element +=  '</div>';
        jQuery("#video_urls").append(div_element);
        jQuery(".remove_video").click(remove_video);
    }
	
	function add_link(){
		link_id +=1;
		var title_label_tag = "<label>Title: </label>";
		var title_tag = "<input type=\"text\" name=\"link_title\"></input>";
		var url_label_tag = "<label>Url: </label>";
		var url_tag = "<input type=\"text\" name=\"link_url\"></input>";
		var div_tag = "<div id=\"link_" + link_id + "\">" + title_label_tag + title_tag + url_label_tag + url_tag + "</div>";
		jQuery("#project-links").append(div_tag);
	}
	
	function remove_video(){
	    var video_url_count = jQuery(".add_video_url").length;
	    if(video_url_count==2){
	        jQuery("#remove_video_1").remove();
	        jQuery("#video_url_1 input[type='radio']").remove();
	    }
	    jQuery("#video_url_" + this.id.split("_")[2]).remove();
	}
	
	function plot_project(){
	    lat = jQuery("#id_latitude")[0].value;
        lon = jQuery("#id_longitude")[0].value;
        if(!is_empty(lat) && !is_empty(lon)){
            markers.destroy();
            markers = new OpenLayers.Layer.Markers( "Markers" );
            map.addLayer(markers);
            var marker_icon = icon.clone();
            marker = new OpenLayers.Marker(
                                new OpenLayers.LonLat(lon, 
                                            lat),marker_icon);
            markers.addMarker(marker);
        }
	}
	
	function is_empty(string){
	    var s = string.trim();
	    return s=="" || s==null;
	}
	
	jQuery("#project-links").html(project_links);
    jQuery("#add_link").click(add_link);
    jQuery("#add_video").click(add_video);
    jQuery(".remove_video").click(remove_video);
    
    jQuery("#id_latitude").blur(function () {
        plot_project();
    });
    jQuery("#id_longitude").blur(function () {
        plot_project();
    });
	
	jQuery('.file-remove-edit').click(function(){
		var filename = jQuery(this).prev().prev().html();
		jQuery.get("/remove_attachment/", {'project_id' : project_id, 'file-name' : filename});
		jQuery(this).parent().remove();
		return false;
	});
	
	jQuery('.photo-remove-edit').click(function(){
		var filename = jQuery(this).prev().html();
		jQuery.get("/remove_photo/", {'project_id' : project_id, 'file-name' : filename});
		jQuery(this).prev().remove();
		jQuery(this).remove();
		jQuery("#photo-attach").show();
		return false;
	});
	
	jQuery(".delete_comment").click(function(){
        var url = "/projects/comments/delete/";
        var span_id = this.id;
        var comment_id = span_id.replace("delete_", "");
        data = {};
        data[comment_id] = true;
        jQuery.post(url, data, function(result){
            jQuery("#" + comment_id).remove();
            if(jQuery(".comment_metainfo").size() === 0){
                jQuery(".comments_header").hide();
            }
        });
    });
	
});
