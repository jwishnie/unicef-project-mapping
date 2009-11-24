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

	
	function add_link(){
		link_id +=1;
		var title_label_tag = "<label>Title: </label>";
		var title_tag = "<input type=\"text\" name=\"link_title\"></input>";
		var url_label_tag = "<label>Url: </label>";
		var url_tag = "<input type=\"text\" name=\"link_url\"></input>";
		var div_tag = "<div id=\"link_" + link_id + "\">" + title_label_tag + title_tag + url_label_tag + url_tag + "</div>";
		jQuery("#project-links").append(div_tag);
	}
	
	jQuery("#project-links").html(project_links);
	
	jQuery("#add_link").click(add_link);
	
	jQuery('.file-remove-edit').click(function(){
		var filename = jQuery(this).prev().prev().html();
		jQuery.get("/remove_attachment/", {'project_id' : project_id, 'file-name' : filename});
		jQuery(this).parent().remove();
		return false;
	});
	
	jQuery(".delete_comment").click(function(){
        var url = "/projects/comments/delete/";
        comment_id = this.id;
        jQuery.post(url, {comment_id : true}, function(data){
                            jQuery("#" + comment_id).remove();
                        });
    });
	
});
