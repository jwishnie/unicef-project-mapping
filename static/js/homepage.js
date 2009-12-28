function collapseProjects() {
    $('ul.sectors_and_implementors').hide();
    $('li.projects_drawer div').removeClass('expanded');
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

function toggleSpinner(){
    if($("#ajax-spinner").is(":visible")){
        $("#ajax-spinner").hide();
    }else{
        $("#ajax-spinner").show();
    }
}

function constructQueryString(selected_filters) {
    var qstring = "";
    for (var i = 0; i < selected_filters.length; i++) {
        qstring += "&" + selected_filters[i].name + "=true";
    }
    return qstring;
}

function populateRegionStats(response) {
    $.get("/search_admin_unit/", {
        text: response.responseText
    },
    function(data) {
        var statistics = JSON.parse(data);
        var statsHtml = " ";
        if (statistics.found) {
            statsHtml = '<ul><li>' + statistics.unit_in_focus + '</li><li> Health :' + statistics.health + '</li><li>Economy :' + statistics.economy + '</li><li>Environment :' + statistics.environment + '</li></ul>';
        } else {
            statsHtml = statistics.unit_in_focus + '<p/>Sorry the data is not found.';
        }
        $("#proj").html(statsHtml);
    });
}

$(document).ready(function() {
    BASE_LAYER = "http://labs.metacarta.com/wms/vmap0";
    MAX_SCALE = 865124.6923828125;
    MIN_SCALE = 130000000;

    var active_kml_layers = new Object();
    active_kml_layers["Markers"] = true;
    var regional_data_layers = {};
    // pink tile avoidance
    OpenLayers.IMAGE_RELOAD_ATTEMPTS = 5;
    // make OL compute scale according to WMS spec
    OpenLayers.DOTS_PER_INCH = 25.4 / 0.28;

    hideFilterableCriteria();

    
    $("li#share_li").click(function() {
        bookmarkUrl();
        $('#bookmark').show();
        $('#main_content').css('opacity','0.5');
        $('#header').css('opacity','0.5');
        $('#main_nav').css('opacity','0.5');
    });
    
    $("#bookmark_close").click(bookmarkClose);
    
    function bookmarkClose(){
        $('#bookmark').hide();
        $('#main_content').css('opacity','1');
        $('#header').css('opacity','1');
        $('#main_nav').css('opacity','1');        
        $('#bookmark').html("<div id='bookmark_close'>Use this URL to share</div>");
        $("#bookmark_close").click(bookmarkClose);
    }
    
    $('#filterable_criteria li.sectors_li').click(function() {
        if($('ul.sector_drawer').is(":visible")) {
            clearRegionalDataLayers();
            collapseSectors();
        }else {
            clearRegionalDataLayers();
            expandSectors();
        }
    });
    
    $('#filterable_criteria li.implementors_li').click(function() {
        if($('ul.implementor_drawer').is(":visible")) {
            clearRegionalDataLayers();
            collapseImplementors();
        }else {
            clearRegionalDataLayers();
            expandImplementors();
        }
    });
    
    $('#filterable_criteria li.projects_drawer div').click(function() {
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseOverlays();
        }
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseRegionData();
        }
        if ($('#filterable_criteria li.projects_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseProjects();
            hideMarkers();
        }else {
            clearRegionalDataLayers();
            expandProjects();
            showMarkers();
        }
    });
 
    $('#filterable_criteria li.overlay_drawer div').click(function() {
        if ($('#filterable_criteria li.projects_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseProjects();
            hideMarkers();
        }
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseRegionData();
        }
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseOverlays();
        } else {
            clearRegionalDataLayers();
            expandOverlays();
            showOverlays();
        }
    });
 
    $('#filterable_criteria li.regiondata_drawer div').click(function() {
        if ($('#filterable_criteria li.projects_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseProjects();
            hideMarkers();
        }
        if ($('#filterable_criteria li.overlay_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseOverlays();
        }
        if ($('#filterable_criteria li.regiondata_drawer span.open').size() !== 0) {
            clearRegionalDataLayers();
            collapseRegionData();
        }else {
            clearRegionalDataLayers();
            expandRegionData();
            switchStatsView();
        }
    });   

    function clearRegionalDataLayers() {
        var layers = map.layers;
        $.each(active_kml_layers, function(layer_name, val) {
            var visible_layer = map.getLayersByName(layer_name)[0];
            if (visible_layer) {
                visible_layer.setVisibility(false);
            }
        });
        $.each(layers, function() {
            if (regional_data_layers[this.name]) {
                map.removeLayer(this);
            }
        });
        $.each(layers, function() {
            if (this.name.contains(":")) {
                map.removeLayer(this);
            }
        });
        var world = map.getLayersByName("World");
        $.each(world, function() {
            map.removeLayer(this);
        });

        $(layers, function() {
            if (this.name.contains(":")) {
                $("#" + this.replace(":", "_")).remove();
                delete regional_data_layers[this];
            }
        });

        regional_data_layers = {};
        map.events.unregister('moveend', map, mapEvent);

        map.zoomToScale(0);
        $("#proj").html("");
        $("input[value=World]:radio").attr("checked", "checked");
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
        $('#bookmark').append(url);
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
    }

    function showOverlays() {
        toggleSpinner();
        var checked_overlays = $(".overlaybox:checked");
        $.each(checked_overlays, function() {
            kml_id = this.value;
            layer_name = "kml_" + kml_id;
            kml_filename = $("#" + layer_name).html();
            if (layer_name in active_kml_layers) {
                var visible_layer = map.getLayersByName(layer_name)[0];
                if (visible_layer) {
                    visible_layer.setVisibility(true);
                }
            } else {
                $("[name=" + layer_name + "]").attr("checked", false);
            }
        });
        toggleSpinner();
    }
    
    function handleOverlays() {
        kml_id = this.value;
        layer_name = "kml_" + kml_id;
        if (this.checked) {
            kml_filename = $("#" + layer_name).html();
            if (layer_name in active_kml_layers) {
                var visible_layer = map.getLayersByName(layer_name)[0];
                if (visible_layer)
                {
                    visible_layer.setVisibility(true);
                }
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
        $("input[value=World]:radio").attr("checked", "checked");
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
        map.events.register('click', map, handleRegionDataClick);
    }

    function layerClickedOn() {
        layersInMap = map.layers;
        $.each(layersInMap,
        function() {
            if (!this.isBaseLayer) {
                if (this.visibility) {
                    layerToQuery = this.params.LAYERS;
                }
            }
        });
        return layerToQuery;
    }

    function handleRegionDataClick(event) {
        if (layerClickedOn() === 'GADM:World') {
            queryCountryClickedOn(event);
        }
        else {
            queryForRegionData(event);
        }
    }

    function queryCountryClickedOn(e) {
        layerClickedOn();
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
        $.each(regional_data_layers, function(key,val) {
            $("#" + key.replace(":", "_")).remove();
            delete regional_data_layers[key];
        });
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
                        var htmlLayer = '<div id=' + this.replace(":", "_") + '><li><input type="radio" name="layergroup" value="' + this + '" class="radiolayer"/><label>' + this.split(":")[1] + '</label></li><p/></div>';
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
});
