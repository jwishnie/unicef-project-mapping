jQuery(document).ready(function(){
    $(".delete_comment").click(function(){
        var url = "/projects/comments/delete/";
        var span_id = this.id;
        var comment_id = span_id.replace("delete_", "");
        data = {};
        data[comment_id] = true;
        data['project_id'] = project_id;
        $.post(url, data, function(result){
            jQuery("#" + comment_id).remove();
            if(jQuery(".comment_metainfo").size() === 0){
                jQuery(".comments_header").hide();
            }
        });
    });
})