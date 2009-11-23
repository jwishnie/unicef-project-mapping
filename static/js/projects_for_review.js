jQuery(document).ready(function(){
	$('.publish_link').click(function(){
		project_id = (this.id).split("_")[1];
		var url = "/projects/publish/" + project_id +"/";
		var tr_id = "#project_" + project_id;
		$.get(url, function(data){
			$(tr_id).remove();
		});	
	});
	
	$('.reject_link').click(function(){
		project_id = (this.id).split("_")[1];
		var url = "/projects/reject/" + project_id +"/";
		var tr_id = "#project_" + project_id;
		$.get(url, function(data){
			$(tr_id).remove();
		});	
	});
	
	$('.delete_link').click(function(){
		project_id = (this.id).split("_")[1];
		delete_url = "/projects/delete/" + project_id +"/";
		delete_tr = "#project_" + project_id;
		$('#delete_dialog').dialog('open');
	});
	
	$("#delete_dialog").dialog({
		bgiframe: true,
		autoOpen: false,
		height: 200,
		width: 300,
		modal: true,
		buttons: {
			Submit: function() {
				$.post(delete_url, function(data){
					$(delete_tr).remove();
				});
				$(this).dialog('close');
			},
			Cancel: function() {
				$(this).dialog('close');
			}
		},
		close: function() {
		}
	});
	
	$("#dialog").dialog({
		bgiframe: true,
		autoOpen: false,
		height: 300,
		width: 400,
		modal: true,
		buttons: {
			Submit: function() {
				var project_id = $("#project_feedback input")[0].value;
				var feedback = $("#project_feedback textarea")[0].value;
				var tr_id = "#project_" + project_id;
				var url = "/request_changes/" + project_id + "/";
				var dialog_box = this;
				$.post(url, {"feedback" : feedback}, function(data){
					var result = JSON.parse(data);
					if(result.authorized){
						if(!result.error){
							$(tr_id).remove();
						}
						else{
							var error = '<div class="error">Feedback is required</div>';
							$("#project_feedback").append(error);
							return;
						}
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
			if($(".error")){
				$(".error").remove();
			}
		}
		
	});

	$('.review_suggestions').click(function() {
		project_id = (this.id).split("_")[1];
		$("#project_feedback").append('<input type="hidden" name="project" value="' + project_id + '"></input>');
		$(".ui-dialog-titlebar-close").html("X");
		$(".ui-dialog-titlebar-close").css("color", "#0C7094");
		$('#dialog').dialog('open');
	});

});