function indicateCurrentLi(){
    main_nav_lis = jQuery("#main_nav ul li a");
    jQuery.each(main_nav_lis, function() {
        var a = this;
        if(a.className == "current_li"){
            a.className = "";
        }
    });

    if(jQuery("#main_pane").size() !== 0) {
        jQuery("#main_nav ul li#home_li a").addClass("current_li");
    }else if(jQuery("#my_projects").size() !== 0) {
        jQuery("#main_nav ul li#my_projs_li a").addClass("current_li");
    }else if(jQuery("#projects_for_review").size() !== 0) {
        jQuery("#main_nav ul li#projs_for_review_li a").addClass("current_li");
    }else if(jQuery("#add_project").size() !== 0) {
        jQuery("#main_nav ul li#add_proj_li a").addClass("current_li");
    }else if(jQuery("#add_admin_unit").size() !== 0) {
         jQuery("#main_nav ul li#add_admin_unit_li a").addClass("current_li");
    }else if(jQuery("#admin_units").size() !== 0) {
        jQuery("#main_nav ul li#admin_units_li a").addClass("current_li");
    }
}

jQuery(document).ready(function() {
    indicateCurrentLi();
    jQuery('#ajax-spinner').hide();
});