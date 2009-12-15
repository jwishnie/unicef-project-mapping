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
	    if(!this.name.startsWith("kml_")){
		    this.checked = 'yes';
	    }
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
        
	$('[name=Search]').click(searchEvent);
    $('#search').focus();
        	
});