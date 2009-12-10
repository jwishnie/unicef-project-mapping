$(document).ready(function(){
    $('.delete_link').click(function(){
		var kml_id = (this.id).split("_")[3];
		var kml_tr_length = this.id.length - 7;
		delete_tr = "#" + (this.id).substr(7, kml_tr_length);
		delete_kml_url = "/delete_kml/" + kml_id +"/";
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
				$.post(delete_kml_url, function(data){
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
})