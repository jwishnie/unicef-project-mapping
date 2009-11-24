$(document).ready(function() {
    $(".publish_comment").click(function(){
        var comments_form = $("#comments_form")[0];
        comments_form.action = "/projects/comments/publish/";
        comments_form.submit();
    });
    
    $(".delete_comment").click(function(){
        var comments_form = $("#comments_form")[0];
        comments_form.action = "/projects/comments/delete/";
        comments_form.submit();
    });
    
});