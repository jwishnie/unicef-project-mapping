jQuery(document).ready(function(){
	$('.delete_link').click(function(){
		admin_unit_id = (this.id).split("_")[1];
		delete_url = "/delete_admin_unit/";
		delete_tr = "#admin_unit_" + admin_unit_id;
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
				$.post(delete_url, {'id' : admin_unit_id}, function(data){
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
});
