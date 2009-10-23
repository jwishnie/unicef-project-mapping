$(document).ready(function() {
    $('li.drawer ul:not(:first)').hide();
    $('h3.drawer-handle').click(function() {
        $('li.drawer ul:visible').slideUp().prev().removeClass('open');
        $(this).addClass('open').next().slideDown();
    });

    $('.sectorbox').click(mapEvent);
    $('.implementorbox').click(mapEvent);


    function mapEvent(event) {
        var boundingBox = map.getExtent();
        var projects_url = "/projects/bbox/" + boundingBox.left + "/" +
        boundingBox.bottom + "/" + boundingBox.right + "/" + boundingBox.top + "/";
        var filters = {};
        $(".sectors input[type=checkbox][checked]").each(function() {
            filters[$(this).attr('name')] = true;
        });
        $(".implementors input[type=checkbox][checked]").each(function() {
            filters[$(this).attr('name')] = true;
        });

        $.post(projects_url, filters,
        function(data) {
            $("#projects").html(data);
        })
    }

    var map = new OpenLayers.Map('map_canvas', {
        eventListeners: {
            "moveend": mapEvent
        }
    });

    var layer = new OpenLayers.Layer.WMS("OpenLayers WMS",
    "http://labs.metacarta.com/wms/vmap0", {
        layers: 'basic'
    });
    map.addLayer(layer);

    map.setCenter(new OpenLayers.LonLat(0, 0), 2);
    var markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(markers);

    var size = new OpenLayers.Size(10, 17);
    var offset = new OpenLayers.Pixel( - (size.w / 2), -size.h);
    var icon = new OpenLayers.Icon('http://labs.google.com/ridefinder/images/mm_20_blue.png', size, offset);

    { %
        for project in projects %
    }
    markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat({
        {
            project.longitude
        }
    },
    {
        {
            project.latitude
        }
    }), icon.clone()));
    { % endfor %
    }

});
