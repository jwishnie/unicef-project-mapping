function collapseSectors() {
    $('ul.sectors').hide();
    $('li.sector_drawer div').removeClass('expanded');
    $('li.sector_drawer div').css("background-color", "#007BD6");
    $('li.sector_drawer span').removeClass('open');
}

function expandSectors() {
    $('ul.sectors').show();
    $('li.sector_drawer div').addClass('expanded');
    $('ul.sectors').css("background-color", "#FFF");
    $('ul.sectors').css("color", "#000");
    $('li.sector_drawer span').addClass('open');
}


function adjustStylesAfterExpand() {
    $('#left_pane').css("width", "170px");
    $('#map_canvas').css("width", "800px");
    $('.expandable_content').show();
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
    $('ul.overlays').css("background-color", "#FFF");
    $('ul.overlays').css("color", "#000");
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
    $('ul.regiondata').css("background-color", "#FFF");
    $('ul.regiondata').css("color", "#000");
    $('li.regiondata_drawer span').addClass('open');
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
    MIN_SCALE = 200000000;

    var active_kml_layers = new Object();
    active_kml_layers["Markers"] = true;
    var regional_data_layers = {};
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
    
    $('#filterable_criteria li.sector_drawer div').click(function() {
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            clearRegionDataLayers();
            collapseOverlays();
            collapseRegionData();
            showMarkers();
        } else {
            clearRegionDataLayers();
            collapseOverlays();
            collapseRegionData();
            hideMarkers();
        }
        if ($('#filterable_criteria li.sector_drawer span.open').size() !== 0) {
            clearRegionDataLayers();
            collapseSectors();
            collapseRegionData();
            hideMarkers();
        }
        else {
            clearRegionDataLayers();
            expandSectors();
            collapseRegionData();
            showMarkers();
        }
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            clearRegionDataLayers();
            collapseOverlays();
            collapseRegionData();
            showMarkers();
        } else {
            clearRegionDataLayers();
            collapseOverlays();
            collapseRegionData();
            hideMarkers();
        }
    });

    $('#filterable_criteria li.overlay_drawer div').click(function() {
        if ($('#filterable_criteria li.sector_drawer span.open').size() !== 0) {
            clearRegionDataLayers();
            collapseSectors();
            collapseRegionData();
            hideMarkers();
        } else {
            clearRegionDataLayers();
            expandSectors();
            collapseRegionData();
            showMarkers();
        }
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            clearRegionDataLayers();
            collapseOverlays();
            collapseRegionData();
            showMarkers();
        }
        else {
            clearRegionDataLayers();
            expandOverlays();
            collapseRegionData();
            hideMarkers();
        }
    });

    $('#filterable_criteria li.regiondata_drawer div').click(function() {
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            clearRegionDataLayers();
            collapseRegionData(); 
            collapseOverlays();
            collapseSectors();
            hideMarkers();
        }
        else {
            clearRegionDataLayers();
            expandRegionData(); 
            collapseOverlays();
            collapseSectors();
            hideMarkers();
            switchStatsView();
        }
    });

    function clearRegionDataLayers() {
        var layers = map.layers;
        $.each(layers, function() {
            if (regional_data_layers[this.name]) {
                map.removeLayer(this);
            }
        });
        var world = map.getLayersByName("World");
        $.each(world, function() {
            map.removeLayer(this);
        });
        regional_data_layers = {};
        //map.zoomToExtent(-180, -90, 180, 90);
    }

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
        $(".sectors input[type=checkbox]:checked").each(function() {
            filters[$(this).attr('name')] = true;
        });
        $(".implementors input[type=checkbox]:checked").each(function() {
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

    $('ul.regiondata').bind('click', switchStatsView);
    var gs = "http://"+window.location.host+"/geoserver/ows";
    
    var worldLayer = new OpenLayers.Layer.WMS(
                "World",
                gs,
                { 
                   layers: 'GADM:World',
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

    function getLayerName(layername) {
        if (layername.search(":") >= 0) {
            return layername.split(":")[1]
        }
        return layername;
    }

    function switchStatsView() {
        $('ul.regiondata').unbind('click', switchStatsView);
        map.events.unregister('moveend', map, mapEvent);
        var bounds = new OpenLayers.Bounds(-180, -90, 180, 90);
        map.zoomToExtent(bounds);
        hide_all_kml_layers();
        toggleSpinner();
        map.addLayer(worldLayer);
        toggleSpinner();
        var layersInMap = map.layers;
        $(".regiondata").html("");
        $("#proj").html("Click on any country to zoom into administrative unit");
        $.each(layersInMap,
        function() {
            if (!this.isBaseLayer) {
                if (! (this.name in active_kml_layers) && ! (this.name in regional_data_layers)) {
                    var isChecked = "";
                    if (this.visibility) {
                        isChecked = 'checked="checked"';
                    }
                    var htmlLayer = '<li><input type="radio" name="layergroup" value="' + this.name + '" class="radiolayer"' + isChecked + '" /><label>' + getLayerName(this.name) + ' (Choose to clear all layers)</label></li><p/>';
                    $(".regiondata").append(htmlLayer);
                    $(".radiolayer").bind('click', switchLayer);
                }
            }
        });
        $("input[name=World]:radio").attr("checked", "checked");
        map.events.register('click', map, queryCountryClickedOn);
    }

    function queryCountryClickedOn(e) {
        toggleSpinner();
        var layersInMap = map.layers;
        $.each(layersInMap, function(){
            if(! this.isBaseLayer){
                if(this.visibility) {
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
        request = response.responseText.split("--------------------------------------------")[1];
	$.get("/country_details/",{text:request},
	    function(data){
	        var bbox = JSON.parse(data);
                var bounds= new OpenLayers.Bounds(bbox.west, bbox.south, bbox.east, bbox.north);    
                map.zoomToExtent(bounds);
                $("#proj").html(bbox.country);
                if(bbox.admin_units instanceof Array) {
                $.each(bbox.admin_units, function() {
                    if (! regional_data_layers[this]) {
                        regional_data_layers[this] = true;
                        var htmlLayer = '<li><input type="radio" name="layergroup" value="' + this + '" class="radiolayer"/><label>' + this.split(":")[1] + '</label></li><p/>';
                        $(".regiondata").append(htmlLayer);
                        $(".radiolayer").bind('click', switchLayer);
                    }
                });
                } else {
                    $("#proj").append("<p>Unfortunately no region data is available for this country</p>");
                }
                toggleSpinner();
	    });
    }

    function projectview() {
        map.zoomToScale(0);
        $("#filterable_criteria").show();
        $("#layercontrols").hide();
        show_all_kml_layers();
        map.addLayer(markers);
        $('#regiondata').bind('click', switchStatsView);
        $('#proj-id').unbind('click', projectview);
        map.events.register('moveend', map, mapEvent);
        map.events.unregister('click', map, queryForRegionData);
    }

    function is_layer_available_in_map(layername) {
        var layers = map.layers;
        var result = false;
        $.each(layers, function() {
            if (this.name == layername) {
                result = true;
            }
        });
        return result;
    }

    function addToMapIfLayerNotAvailable(layername) {
        if(! is_layer_available_in_map(layername)) {
            var layers = map.layers;
            $.each(layers, function () {
               if (! this.isBaseLayer) {
                   this.setVisibility(false); 
               }
            });
            
            var layer = new OpenLayers.Layer.WMS(
                        layername,
                        gs,
                        { 
                           layers: layername,
                           transparent: true,
                           format: 'image/png'
                        },
                        {
                           isBaseLayer: false,
                           visibility: true
                        }
            );
            layer.setOpacity(0.5);
            map.addLayer(layer);
        }
    }

    function enableLayerIfAvailable(layerName) {
        var layers = map.layers;
        $.each(layers, function () {
            if (! this.isBaseLayer) {
                this.setVisibility(false);
                if (this.name === layerName) {
                    this.setVisibility(true);
                }
            }
        });
    }

    function switchLayer(event) {
        var layerName = $(this).attr("value");
        var layersInMap = map.layers;
        enableLayerIfAvailable(layerName);
        addToMapIfLayerNotAvailable(layerName);
    }

    function hide_all_kml_layers() {
        for (layer in active_kml_layers) {
            if (active_kml_layers[layer]) {
                var kml_layer = map.getLayersByName(layer)[0];
                kml_layer.setVisibility(false);
            }
        }
    }

    function show_all_kml_layers() {
        for (layer in active_kml_layers) {
            if (active_kml_layers[layer]) {
                var kml_layer = map.getLayersByName(layer)[0];
                kml_layer.setVisibility(true);
            }

        }
    }
});
