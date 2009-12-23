$(document).ready(function() {
    var is_chrome = (/chrome/).test(navigator.userAgent.toLowerCase());
    if(is_chrome) {
        OpenLayers.DOTS_PER_INCH = 1;
    }

	function searchEvent(){
        var text = escape($('[name=q]').val());
        if($.trim(text)) {
	    var search_url = "/projects/search/";
		$.get(search_url);	  
        }
	}
        
	$('[name=Search]').click(searchEvent);
    $('#search').focus();
        	
});