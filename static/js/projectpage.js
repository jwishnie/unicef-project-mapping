$(document).ready(function() {
    var delete_url = "";
    var map;

    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125
    MIN_SCALE = 110735960.625
    WIDTH = 10
    HEIGHT = 17

    $('#photo_set a').lightBox({fixedNavigation:true});
    
    map = new OpenLayers.Map('map_canvas', {
        maxScale: MAX_SCALE,
        minScale: MIN_SCALE
    });
    var layer = new OpenLayers.Layer.VirtualEarth("Hybrid", {
        type: VEMapStyle.Hybrid
    });
    map.addLayer(layer);
    // map.setCenter(new OpenLayers.LonLat(longitude, latitude));
    var bounds = new OpenLayers.Bounds(left, bottom, right, top);
    map.zoomToExtent(bounds);

    var markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(markers);

    var size = new OpenLayers.Size(WIDTH, HEIGHT);
    var offset = new OpenLayers.Pixel( - (size.w / 2), -size.h);
    var icon = new OpenLayers.Icon(imgurl + '/red-marker.png', size, offset);
    markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(longitude,
                                            latitude), icon.clone()));

    addsubprojects(markers);

    $("#published_comment").dialog({
        bgiframe: true,
        autoOpen: false,
        height: 300,
        width: 400,
        modal: true,
        buttons: {
            Submit: function() {
                $(".errorlist").remove();
                var name = $("#id_username")[0].value;
                var email = $("#id_email")[0].value;
                var comment = $("#id_text")[0].value;
                var project_id = $("#comment_project_id")[0].value;

                var data = {
                    "name": name,
                    "email": email,
                    "comment": comment
                };
                var url = "/projects/" + project_id + "/comment/";
                var dialog_box = this;

                $.post(url, data,
                function(result) {
                    var result = JSON.parse(result);
                    if (result.message != null) {
                        $('#comment_message').html(result.message);
                        $('#comment_message').css("background-color", "#ECE5B6");
                        $(dialog_box).dialog('close');
                    }else{
                        print_comment_error_messages(result);
                    }
                });
            },
            Cancel: function() {
                $(this).dialog('close');
            }
        },
        close: function() {
            $(".errorlist").remove();
        }

    });

    $('#comment_link').click(function() {
        $(".ui-dialog-titlebar-close").html("X");
        $(".ui-dialog-titlebar-close").css("color", "#0C7094");
        $('#published_comment').dialog('open');
        $("#published_comment").css("height", "auto");
        styleDialogBox();
    });
    
    function styleDialogBox(){
        var doc_height = document.body.offsetHeight;
        var ui_dialog_height = 425;
        var top = doc_height - ui_dialog_height - 100;
        
        $(".ui-dialog").css("top", top+"px");
        $(".ui-dialog").css("width", "450px");
        $(".ui-widget-overlay").css("z-index", "1005");
        $(".ui-dialog").css("z-index", "1006");    
    }
    
    function reset_publish_link(message, project_id){
        var action = (message=="Published" ? "unpublish" : "publish");
        var html_text =  action + '<input type="hidden" value="/projects/' + 
                    action +'/' + project_id + '/" name="link"/>';
        var span_id = "#publish_" + project_id;
        $(span_id).html(html_text);
        var message = "Project " + message + " Successfully";
        $("#publish_message").html(message);
        $("#publish_message").css("background-color", "#ECE5B6");
    }
    
    function print_comment_error_messages(errors){
        var error_list="";
        if(errors.username){
            error_list = '<ul class="errorlist"><li>' + errors.username + '</li></ul>';
            $("#id_username").after(error_list);
        }
        if(errors.email){
            error_list = '<ul class="errorlist"><li>' + errors.email + '</li></ul>';
            $("#id_email").after(error_list);
        }
        if(errors.comment){
            error_list = '<ul class="errorlist"><li>' + errors.comment + '</li></ul>';
            $("#id_text").after(error_list);
        }
    }

    $(".publish_link").click(function() {
        var publish_link = $(".publish_link input")[0].value;
        $.get(publish_link,
        function(data) {
            var result = JSON.parse(data);
            reset_publish_link(result.message, result.id);
        });
    });
    
    $('.delete_link').click(function(){
        project_id = (this.id).split("_")[1];
        delete_url = "/projects/delete/" + project_id +"/";
        $('#delete_dialog').dialog('open');
	});
	
	$("#delete_dialog").dialog({
		bgiframe: true,
		autoOpen: false,
		height: 200,
		width: 300,
		modal: true,
		buttons: {
			Submit: function() {
				$.post(delete_url, function(data){
					window.location.href = "/";
				});
				$(this).dialog('close');
			},
			Cancel: function() {
				$(this).dialog('close');
			}
		},
		close: function() {
		}
	});
	
	$('#nearby_projects').click(get_nearby_projects);
	
	function addsubprojects(markers) {
        for (var i = 0; i < projects.length; i++) {
            subproject = projects[i];
            var size = new OpenLayers.Size(WIDTH, HEIGHT);
            var offset = new OpenLayers.Pixel( - (size.w / 2), -size.h);
            var icon = new OpenLayers.Icon(imgurl + '/bright_red_marker.png', size, offset);
            markers.addMarker(new OpenLayers.Marker
            (new OpenLayers.LonLat(subproject['longitude'],
            subproject['latitude']), icon.clone()));
        }
    }


    function get_nearby_projects(){
        var text = $('#nearby_projects').html();
        var action = text.substring(0, 4);
        if(action == "Show"){
            $('#nearby_projects').html("Hide projects around this location");
            var boundingBox = map.getExtent();
        	var projects_url = "/projects/bbox/" + boundingBox.left + "/" + 
        						boundingBox.bottom + "/" + boundingBox.right + "/" + boundingBox.top + "/";

        	$.get(projects_url, function(data) {
                    var projects = JSON.parse(data);
                    addProjectsOnMap(projects);
            });
            
        }else{
            $('#nearby_projects').html("Show projects around this location");
            markers.destroy();
            markers = new OpenLayers.Layer.Markers( "Markers" );
            map.addLayer(markers);
            markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(longitude,
                                                    latitude), icon.clone()));
            addsubprojects(markers);
        }
    }


    function addProjectsOnMap(projects) {
        // var html = "<ul>";
        for(var i = 0;i<projects.length; i++){
            var project = projects[i];
            // var project_name = project.snippet.split(":")[0];
            //       var project_description = project.snippet.split(":")[1];               
            //       var project_text = "<a href=\"/projects/id/" + project.id + "/" +"\">" + 
            //                                   project_name + '</a><div class="proj_desc">' +  project_description;
            //       html += "<li>" + project_text + "</li>";
            var marker_icon = icon.clone();
            marker = new OpenLayers.Marker(
                                new OpenLayers.LonLat(project.longitude, 
                                            project.latitude),marker_icon);
            // marker.events.register("mousedown", {'marker' : marker, 'text' : project_text}, mousedn);
            markers.addMarker(marker);
        }
        // html += "</ul></div>";
        // $("#proj").html(html);
    }

});






