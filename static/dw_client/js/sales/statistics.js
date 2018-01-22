$(document).ready(function(){
    $('table:last').after($('.pagination').clone());
    $('.pagination > li > a').click(function(event){
        event.preventDefault();

        $.get(
            form_sales_statistics_url(
                from_date_input.val(),
                to_date_input.val(),
                parseInt($(this).attr('href'))
            ),
            function(data){
                $('#statistics').html(data);
            }
        );
    });
    $('.pagination > li.disabled > a').off("click").removeAttr('href');
});
