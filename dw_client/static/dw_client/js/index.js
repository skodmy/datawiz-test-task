$(document).ready(function(){
    // hardcoded
    window.circular_preloader_html = "" +
        "<div class=\"preloader-wrapper big active\">\n" +
        "    <div class=\"spinner-layer spinner-blue-only\">\n" +
        "        <div class=\"circle-clipper left\">\n" +
        "            <div class=\"circle\"></div>\n" +
        "        </div>\n" +
        "        <div class=\"gap-patch\">\n" +
        "            <div class=\"circle\"></div>\n" +
        "        </div>\n" +
        "        <div class=\"circle-clipper right\">\n" +
        "            <div class=\"circle\"></div>\n" +
        "        </div>\n" +
        "    </div>\n" +
        "</div>\n";

    $('#account_menu, #account_menu_mobile').find('li > a').addClass('deep-purple-text');
    $('.dropdown-button').dropdown();
    $('.sidenav').sidenav();
});
