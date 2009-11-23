$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125
    MIN_SCALE = 110735960.625
    WIDTH = 10
    HEIGHT = 17

    var map = new OpenLayers.Map('map_canvas', {
        maxScale: MAX_SCALE,
        minScale: MIN_SCALE
    });
    var layer = new OpenLayers.Layer.WMS("OpenLayers WMS",
    BASE_LAYER, {
        layers: 'basic'
    });
    map.addLayer(layer);


    map.setCenter(new OpenLayers.LonLat(longitude, latitude));
    var markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(markers);

    var size = new OpenLayers.Size(WIDTH, HEIGHT);
    var offset = new OpenLayers.Pixel( - (size.w / 2), -size.h);
    var icon = new OpenLayers.Icon(imgurl + '/red-marker.png', size, offset);
    markers.addMarker(new OpenLayers.Marker
    (new OpenLayers.LonLat(longitude,
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
                        $(dialog_box).dialog('close');
                    }
                });
            },
            Cancel: function() {
                $(this).dialog('close');
            }
        },
        close: function() {
            $("#project_feedback input[type=\"hidden\"]").remove();
            if ($(".error")) {
                $(".error").remove();
            }
        }

    });

    $('#comment_link').click(function() {
        $(".ui-dialog-titlebar-close").html("X");
        $(".ui-dialog-titlebar-close").css("color", "#0C7094");
        $('#published_comment').dialog('open');
    });
    
    function reset_publish_link(message, project_id){
        var action = (message=="Published" ? "unpublish" : "publish");
        var html_text =  action + '<input type="hidden" value="/projects/' + 
                    action +'/' + project_id + '/" name="link"/>';
        var span_id = "#publish_" + project_id;
        $(span_id).html(html_text);
        var message = "Project " + message + " Successfully";
        $("#publish_message").html(message);
    }

    $(".publish_link").click(function() {
        var publish_link = $(".publish_link input")[0].value;
        $.get(publish_link,
        function(data) {
            var result = JSON.parse(data);
            reset_publish_link(result.message, result.id);
        });
    });
    
    $(".delete_link").click(function(){
        var project_id = (this.id).split("_")[1];
        var delete_url = "/projects/delete/" + project_id + "/";
        $.post(delete_url, function(data){
            window.location.href = "/";
        });
    });


}
);
function addsubprojects(markers) {
    for (var i = 0; i < projects.length; i++) {
        subproject = projects[i];
        var size = new OpenLayers.Size(WIDTH, HEIGHT);
        var offset = new OpenLayers.Pixel( - (size.w / 2), -size.h);
        var icon = new OpenLayers.Icon(imgurl + '/mini-blue-marker.png', size, offset);
        markers.addMarker(new OpenLayers.Marker
        (new OpenLayers.LonLat(subproject['longitude'],
        subproject['latitude']), icon.clone()));
    }
}
