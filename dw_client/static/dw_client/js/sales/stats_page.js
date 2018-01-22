$(document).ready(function(){
    // definition stuff
    // global
    // making that function globaly available for its usage in other scripts(statistics.js)
    window.form_sales_statistics_url = function (date_from, date_to, page_number){
        return '/dw-client/sales/statistics/' +
            date_from +
            '--' +
            date_to +
            (!page_number? '/1/' : '/' + page_number + '/')
    };
    // local
    var datepickers = $('input[name^="date"]').addClass('validate datepicker');

    function to_ints_array(date_str){
        var ints = [];
        date_str.split('-').forEach(function(element, index){
            ints[index] = parseInt(element);
        });
        return ints;
    }

    function validate_dates(date_from, date_to){
        if(to_ints_array(date_from) > to_ints_array(date_to)){
            return [date_to, date_from];
        }
        return [date_from, date_to];
    }

    // initializing stuff
    datepickers.each(function(){
        $(this).datepicker({
            format: 'yyyy-mm-dd',
            yearRange: 3,
            minDate: new Date(2014, 5, 1),
            maxDate: new Date(2015, 10, 18), // there October, but in picker November
            onDraw: function(){
                // customizing look here due to usage of [materialize] defined classes
                $('.datepicker-date-display, .datepicker-table td.is-selected').addClass('deep-purple');
                $('.datepicker-today, .datepicker-done, .dropdown-content li > a, .dropdown-content li > span').addClass('deep-purple-text');
            }
        });
    });

    $('form').submit(function(event){
        event.preventDefault();

        window.from_date_input = $('input[name="date_from"]');
        window.to_date_input = $('input[name="date_to"]');
        var date_from, date_to;
        [date_from, date_to] = validate_dates(from_date_input.val(), to_date_input.val());
        var statistics = $("#statistics");

        from_date_input.val(date_from);
        to_date_input.val(date_to);

        // showing preloader
        statistics.html(circular_preloader_html);

        // ajaxing data
        $.get(
            form_sales_statistics_url(date_from, date_to),
            function(data){
                statistics.html(data);
            }
        );
    });
});
