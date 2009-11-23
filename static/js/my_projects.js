function update_project(project){
	var review_status = "";
	var result = "<td>"+ project.name +"</td>";
	result += "<td>"+ project.status +"</td>";
	result += "<td><a href=\"/edit_project/" + project.id +"/\">Edit</a></td>";

	if(project.authorized){
		if(project.status == "Published")
	        result += "<td><span class=\"unpublish_link first\" id=\"" + project.id + "\">Unpublish</span></td>";
	    else
	        result += "<td><span class=\"publish_link first\" id=\"" + project.id + "\">Publish</span></td>";
	}
    var tr_id = "#project_" + project.id;
	$(tr_id).html(result);
}

jQuery(document).ready(function(){
	$(".ui-dialog-titlebar-close").html("X");
	$(".ui-dialog-titlebar-close").css("color", "#0C7094");
	
	
	$('.publish_link').click(function(){
		var url = "/projects/publish/" + this.id +"/";
		$.get(url, function(data){
			var project = JSON.parse(data);
			update_project(project);
		});	
	});

	$('.unpublish_link').click(function(){
		var url = "/projects/unpublish/" + this.id +"/";
		$.get(url, function(data){
			var project = JSON.parse(data);
			update_project(project);
		});	
	});
	
	$('.changes_preview').click(function(){
		var project_id = (this.id).split("_")[1];
		var url = "/projects/review_suggestions/" + project_id + "/";
		$.get(url, function(data){
			
			$('#dialog').html(data);
			$('#dialog').dialog('open');
		});

	});
	
	
	$("#dialog").dialog({
		bgiframe: true,
		autoOpen: false,
		height: 300,
		width: 400,
		modal: true,
		buttons: {
			Close: function() {
				$(this).dialog('close');
			}
		},
		close: function() {
			$("#project_feedback input[type=\"hidden\"]").remove();
			if($(".error")){
				$(".error").remove();
			}
		}
	});
});