function collapseProjects() {
    $('ul.sectors_and_implementors').hide();
    $('li.projects_drawer div').removeClass('expanded');
    $('li.projects_drawer div').css("background-color", "#007BD6");
    $('li.projects_drawer span').removeClass('open');
}

function expandProjects() {
    expandSectors();
    expandImplementors();
    $('ul.sectors_and_implementors').show();
    $('li.projects_drawer div').addClass('expanded');
    $('li.projects_drawer span').addClass('open');
}

function collapseOverlays() {
    $('ul.overlays').hide();
    $('li.overlay_drawer div').removeClass('expanded');
    $('li.overlay_drawer div').css("background-color", "#007BD6");
    $('li.overlay_drawer span').removeClass('open');
}

function expandOverlays() {
    $('ul.overlays').show();
    $('li.overlay_drawer div').addClass('expanded');
    $('li.overlay_drawer span').addClass('open');
}

function collapseRegionData() {
    $('ul.regiondata').hide();
    $('li.regiondata_drawer div').removeClass('expanded');
    $('li.regiondata_drawer div').css("background-color", "#007BD6");
    $('li.regiondata_drawer span').removeClass('open');
}

function expandRegionData() {
    $('ul.regiondata').show();
    $('li.regiondata_drawer div').addClass('expanded');
    $('li.regiondata_drawer span').addClass('open');
}

function collapseSectors() {
    $('ul.sector_drawer').hide();
    $('ul.sectors_and_implementors li.sectors_li').removeClass('expanded');
}

function expandSectors() {
    $('ul.sector_drawer').show();
    $('ul.sectors_and_implementors li.sectors_li').addClass('expanded');
}

function collapseImplementors() {
    $('ul.implementor_drawer').hide();
    $('ul.sectors_and_implementors li.implementors_li').removeClass('expanded');
}

function expandImplementors() {
    $('ul.implementor_drawer').show();
    $('ul.sectors_and_implementors li.implementors_li').addClass('expanded');
}

function hideFilterableCriteria() {
    $('#filterable_criteria ul.overlays').hide();
}

function populateRegionStats(response) {
    $.get("/search_admin_unit/", {
        text: response.responseText
    },
    function(data) {
        var statistics = JSON.parse(data);
        var statsHtml = " ";
        if (statistics.found) {
            statsHtml = '<ul><li> Health :' + statistics.health + '</li><li>Economy :' + statistics.economy + '</li><li>Environment :' + statistics.environment + '</li></ul>';
        } else {
            statsHtml = 'Sorry the data is not found.';
        }
        $("#stats").html(statsHtml);
    });
}

$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125;
    MIN_SCALE = 130000000;

    var active_kml_layers = new Object();
    active_kml_layers["Markers"] = true;
    // pink tile avoidance
    OpenLayers.IMAGE_RELOAD_ATTEMPTS = 5;
    // make OL compute scale according to WMS spec
    OpenLayers.DOTS_PER_INCH = 25.4 / 0.28;

    hideFilterableCriteria();
    
    function toggleSpinner(){
        if($("#ajax-spinner").is(":visible")){
            $("#ajax-spinner").hide();
        }else{
            $("#ajax-spinner").show();
        }
    }
    
    $('#filterable_criteria li.sectors_li').click(function() {
        if($('ul.sector_drawer').is(":visible")) {
            collapseSectors();
        }else {
            expandSectors();
        }
    });
    
    $('#filterable_criteria li.implementors_li').click(function() {
        if($('ul.implementor_drawer').is(":visible")) {
            collapseImplementors();
        }else {
            expandImplementors();
        }
    });
    
    $('#filterable_criteria li.projects_drawer div').click(function() {
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            collapseOverlays();
        }
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            collapseRegionData();
        } 
        if ($('#filterable_criteria li.projects_drawer span.open').size() !== 0) {
            collapseProjects();
            hideMarkers();
        }else {
            expandProjects();
            showMarkers();
        }
    });

    $('#filterable_criteria li.overlay_drawer div').click(function() {
        if ($('#filterable_criteria li.projects_drawer span.open').size() !== 0) {
            collapseProjects();
            hideMarkers();
        }
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            collapseRegionData();
        }
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            collapseOverlays();
        }else {
            expandOverlays();
        }
    });

    $('#filterable_criteria li.regiondata_drawer div').click(function() {
        if ($('#filterable_criteria li.projects_drawer span.open').size() !== 0) {
            collapseProjects();
            hideMarkers();
        }
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            collapseOverlays();
        }
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            collapseRegionData();
        }else {
            expandRegionData();
            switchStatsView();
        }
    });

    function hideMarkers() {
        var markerLayer = map.getLayersByName("Markers");
        if (markerLayer.length > 0) {
            $.each(markerLayer,
            function() {
                this.setVisibility(false);
            });
        }
        $("#proj").html("Click on the KML layers to see them on the map.");
    }

    function showMarkers() {
        var markerLayer = map.getLayersByName("Markers");
        if (markerLayer.length > 0) {
            $.each(markerLayer,
            function() {
                this.setVisibility(true);
            });
        }
        mapEvent(null);
    }

    function constructQueryString(selected_filters) {
        var qstring = "";
        for (var i = 0; i < selected_filters.length; i++) {
            qstring += "&" + selected_filters[i].name + "=true";
        }
        return qstring;
    }

    function bookmarkUrl() {
        var queryString = "";
        queryString += constructQueryString($(".sectors_and_implementors input[type=checkbox]:checked"));
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

    function getProjects(data) {
        return JSON.parse(data);
    }

    var size = new OpenLayers.Size(10, 17);
    var offset = new OpenLayers.Pixel( - (size.w / 2), -size.h);
    var icon = new OpenLayers.Icon('/static/img/bright_red_marker.png', size, offset);
    var popup = null;

    function mousedn() {
        if (popup !== null) {
            popup.destroy();
        }
        popup = new OpenLayers.Popup("project",
        this.marker.lonlat,
        new OpenLayers.Size(200, 70),
        this.text,
        true);
        map.addPopup(popup);
    }

    function addProjectsOnMap(projects) {
        markers.destroy();
        markers = new OpenLayers.Layer.Markers("Markers");
        map.addLayer(markers);
        var html = "<ul>";
        for (var i = 0; i < projects.length; i++) {
            var project = projects[i];
            var project_name = project.snippet.split(":")[0];
            var project_description = project.snippet.split(":")[1];
            var project_text = "<a href=\"/projects/id/" + project.id + "/" + "\">" +
            project_name + '</a><div class="proj_desc">' + project_description + '</div>';
            html += "<li>" + project_text + "</li>";
            var marker_icon = icon.clone();
            marker = new OpenLayers.Marker(
            new OpenLayers.LonLat(project.longitude,
            project.latitude), marker_icon);
            marker.events.register("mousedown", {
                'marker': marker,
                'text': project_text
            },
            mousedn);
            markers.addMarker(marker);
        }
        html += "</ul>";
        $("#proj").html(html);
    }

    function mapEvent(event) {
        var boundingBox = map.getExtent();
        var projects_url = "/projects/bbox/" + boundingBox.left + "/" +
        boundingBox.bottom + "/" + boundingBox.right + "/" + boundingBox.top + "/";
        var filters = {};
        $(".sectors_and_implementors input[type=checkbox]:checked").each(function() {
            filters[$(this).attr('name')] = true;
        });

        filters.tag = search_tag;

        $.get(projects_url, filters,
        function(data) {
            var projects = getProjects(data);
            addProjectsOnMap(projects);
        });

        bookmarkUrl();
    }

    
    function handleOverlays() {
        kml_id = this.value;
        layer_name = "kml_" + kml_id;
        if (this.checked) {
            kml_filename = $("#" + layer_name).html();
            if (layer_name in active_kml_layers) {
                var visible_layer = map.getLayersByName(layer_name)[0];
                visible_layer.setVisibility(true);
            } else {
                toggleSpinner();
                var layer_kml = new OpenLayers.Layer.GML(layer_name, kml_filename,
                    {
                        format: OpenLayers.Format.KML,
                        formatOptions: {
                            extractStyles: true,
                            extractAttributes: true,
                            maxDepth: 2
                        }
                    });
                map.addLayer(layer_kml);
                layer_kml.events.register("loadend", layer, toggleSpinner);
            }
            active_kml_layers[layer_name] = true;
        } else {
            active_kml_layers[layer_name] = false;
            var remove_layer = map.getLayersByName(layer_name)[0];
            if (remove_layer != null) {
                remove_layer.setVisibility(false);
            }
        }
    }

    var options = {
        maxScale: MAX_SCALE,
        minScale: MIN_SCALE
    };

    var format = 'image/png';
    var map = new OpenLayers.Map('map_canvas', options);

    var layer = new OpenLayers.Layer.WMS("OpenLayers WMS", BASE_LAYER, {
        layers: 'basic'
    },
    {
        'displayInLayerSwitcher': false
    });
    var markers = new OpenLayers.Layer.Markers("Markers");
    var bounds = new OpenLayers.Bounds(left, bottom, right, top);

    map.events.register('moveend', map, mapEvent);
    map.addLayer(layer);
    map.zoomToExtent(bounds);


    $('.sectorbox').bind('click', mapEvent);
    $('.implementorbox').bind('click', mapEvent);

    $('.overlaybox').click(handleOverlays);

    var gs = "http://"+window.location.host+"/geoserver/ows";
    
    var worldLayer = new OpenLayers.Layer.WMS(
                "World",
                gs,
                { 
                   layers: 'GADM:gadm1_lev0',
                   transparent: true,
                   format: 'image/png'
                },
                {
                   isBaseLayer: false,
                   visibility: true
                }
    );
    worldLayer.setOpacity(0.5);

    function queryForRegionData(e) {
        var layersInMap = map.layers;
        var layerToQuery = "";
        $.each(layersInMap,
        function() {
            if (!this.isBaseLayer) {
                if (this.visibility) {
                    layerToQuery = this.params.LAYERS;
                }
            }
        });
        $("#proj").html("Loading. Please wait...");
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
            format: format
        };
        OpenLayers.loadURL("http://" + window.location.host + "/geoserver/wms", params, this, populateRegionStats, populateRegionStats);
        OpenLayers.Event.stop(e);
    }

    function switchStatsView() {
        map.events.unregister('moveend', map, mapEvent);
        var bounds = new OpenLayers.Bounds(-180, -90, 180, 90);
        map.zoomToExtent(bounds);
        toggleSpinner();
        map.addLayer(worldLayer);
        toggleSpinner();
        var layersInMap = map.layers;
        $(".regiondata").html("");
        $("#proj").html("Click on any country to zoom into administrative unit");
        $.each(layersInMap,
        function() {
            if (!this.isBaseLayer) {
                if (! (this.name in active_kml_layers)) {
                    var isChecked = "";
                    if (this.visibility) {
                        isChecked = 'checked="checked"';
                    }
                    var htmlLayer = '<li><input type="radio" name="layergroup" value="' + this.name + '" class="radiolayer"' + isChecked + '" /><label>' + this.name + '</label></li><p/>';
                    $(".regiondata").append(htmlLayer);
                    $(".radiolayer").bind('click', switchLayer);
                }
            }
        });
        map.events.register('click', map, queryCountryClickedOn);
    }

    function queryCountryClickedOn(e) {
        toggleSpinner();
        var layersInMap = map.layers;
            var layerToQuery = "";
            $.each(layersInMap, function(){
                if(! this.isBaseLayer){
                    if(this.visibility){
                        layerToQuery = this.params.LAYERS;
                    }
                }
            });

        $("#proj").html("Loading. Please wait...");
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
            format: format
            };
        OpenLayers.loadURL("http://"+window.location.host+"/geoserver/wms", params, this, findCountryDetails, findCountryDetails);
        OpenLayers.Event.stop(e);
    }

    function findCountryDetails(response) {
	$.get("/country_details/",{text:response.responseText},
	    function(data){
	        var bbox = JSON.parse(data);
                var bounds= new OpenLayers.Bounds(bbox.west, bbox.south, bbox.east, bbox.north);    
                map.zoomToExtent(bounds);
                $("#proj").html("Country Name - " + bbox.country);
                alert(bbox.admin_units instanceof Array);
                if(bbox.admin_units instanceof Array) {
                $.each(bbox.admin_units, function() {
                    var htmlLayer = '<li><input type="radio" name="layergroup" value="' + this + '" class="radiolayer"/><label>' + this + '</label></li><p/>';
                    $(".regiondata").append(htmlLayer);
                    $(".radiolayer").bind('click', switchLayer);
                });
                } else {
                    $("#proj").append("<p>Unfortunately no region data is available for this country</p>");
                }
                toggleSpinner();
	    });
    }

    function switchLayer(event) {
        var layerName = $(this).attr("value");
        var layersInMap = map.layers;
        var shapeFileName = "";
        $.each(layersInMap,
        function() {
            if (!this.isBaseLayer) {
                if (this.name === layerName) {
                    this.setVisibility(true);
                    shapeFileName = this.params.LAYERS;
                } else {
                    this.setVisibility(false);
                }
            }
        });
        var featureRequestUrl = "http://localhost/geoserver/wfs?request=GetFeature&version=1.1.0&typeName=" + shapeFileName;
        var xml = $.get(featureRequestUrl,
        function(data) {
            upperCorner = $(data).find("gml:lowerCorner");
        },
        "xml");
    }
});
