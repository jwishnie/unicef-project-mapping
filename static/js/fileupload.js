window.addEvent('domready', function() {

    var up = new FancyUpload3.Attach('file-list', '.file-attach, .file-attach-2', {
		path: fancy_uploader_swf,
		url: '/projects/upload/',
		fileSizeMax: 3 * 1024 * 1024,
        data: {'project_id' : project_id},
		verbose: true,

		onSelectFail: function(files) {
			files.each(function(file) {
				new Element('li', {
					'class': 'file-invalid',
					events: {
						click: function() {
							this.destroy();
						}
					}
				}).adopt(
					new Element('span', {html: file.validationErrorMessage || file.validationError})
				).inject(this.list, 'bottom');
			}, this);	
		},

		onFileSuccess: function(file) {
            // new Element('input', {type: 'checkbox', 'checked': true}).inject(file.ui.element, 'top');
			file.ui.element.highlight('#e6efc2');
			file.setRemoveURL("/remove_attachment/");
		},

		onFileError: function(file) {
			file.ui.cancel.set('html', 'Retry').removeEvents().addEvent('click', function() {
				file.requeue();
				return false;
			});

			new Element('span', {
				html: file.errorMessage,
				'class': 'file-error'
			}).inject(file.ui.cancel, 'after');
		},

		onFileRequeue: function(file) {
			file.ui.element.getElement('.file-error').destroy();

			file.ui.cancel.set('html', 'Cancel').removeEvents().addEvent('click', function() {
				file.remove();
				return false;
			});

			this.start();
		}

	});
	
	var photouploader = new FancyUpload3.Attach('photo-list', '.photo-attach, .photo-attach-2', {
   		path: fancy_uploader_swf,
   		url: '/projects/photo_upload/',
   		fileSizeMax: 1 * 1024 * 1024,
        data: {'project_id' : project_id},
   		verbose: true,

   		onSelectFail: function(files) {
   			files.each(function(file) {
   				new Element('li', {
   					'class': 'file-invalid',
   					events: {
   						click: function() {
   							this.destroy();
   						}
   					}
   				}).adopt(
   					new Element('span', {html: file.validationErrorMessage || file.validationError})
   				).inject(this.list, 'bottom');
   			}, this);	
   		},

   		onFileSuccess: function(file) {
               // new Element('input', {type: 'checkbox', 'checked': true}).inject(file.ui.element, 'top');
   			file.ui.element.highlight('#e6efc2');
   			file.setRemoveURL("/remove_photo/");
   			jQuery("#photo-attach").hide();
   		},

   		onFileError: function(file) {
   			file.ui.cancel.set('html', 'Retry').removeEvents().addEvent('click', function() {
   				file.requeue();
   				return false;
   			});

   			new Element('span', {
   				html: file.errorMessage,
   				'class': 'file-error'
   			}).inject(file.ui.cancel, 'after');
   		},

   		onFileRequeue: function(file) {
   			file.ui.element.getElement('.file-error').destroy();

   			file.ui.cancel.set('html', 'Cancel').removeEvents().addEvent('click', function() {
   				file.remove();
   				return false;
   			});

   			this.start();
   		},
   		
   		onFileRemove: function(){
   		    jQuery("#photo-attach").show();
   		}

   	});
	

});