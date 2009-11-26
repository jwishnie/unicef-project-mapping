jQuery(document).ready(function(){

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
	
	
	jQuery("#project-links").html(project_links);
    jQuery("#add_link").click(add_link);
    jQuery("#add_video").click(add_video);
    jQuery(".remove_video").click(remove_video);
    

	
	jQuery('.file-remove-edit').click(function(){
		var filename = jQuery(this).prev().prev().html();
		jQuery.get("/remove_attachment/", {'project_id' : project_id, 'file-name' : filename});
		jQuery(this).parent().remove();
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
