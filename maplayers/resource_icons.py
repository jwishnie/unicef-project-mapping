class ResourceIcon(object):
    RESOURCE_ICONS = {
        'xls' : '/static/img/ms_excel.jpg',
        'xlsx' : '/static/img/ms_excel.jpg',
        'doc' : '/static/img/ms_word.jpg',
        'docx' : '/static/img/ms_word.jpg',
        'ppt' : '/static/img/ms_ppt.jpg',
        'pptx' : '/static/img/ms_ppt.jpg',
        'pdf' : '/static/img/pdf.jpg',
        'mp3' : '/static/img/mp3.jpg',
        'ogg' : '/static/img/ogg.jpg'
    }

    def icon(self, file_extension):
        if self.RESOURCE_ICONS.has_key(file_extension):
            return self.RESOURCE_ICONS[file_extension]
        else:
            return ""
        