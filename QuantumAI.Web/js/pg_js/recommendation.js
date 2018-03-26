
var login_type = 0;
$(document).ready(function ($) {

    "use strict";
    if (localStorage.getItem("is_login") == 0) {
        window.location.href = "/login.html"
    }
    else {
    	$('#menu').find('li[data-login-type="1"]').show();
    	if (localStorage.getItem("is_login") == 2) {
    		$('#menu').find('li[data-login-type="1"]').hide();
    	}
    	login_type = localStorage.getItem("is_login");

        $('.page').show();
        $('.recc_dt_picker').datepicker({
            format: 'dd-M-yyyy',
            autoclose: 'true'

        }).datepicker("setDate", new Date());
        $.getJSON('js/pg_js/aapl-c.json', function (data) {
            // Create the chart
            Highcharts.stockChart('_buygraph-container', {
                rangeSelector: {
                    selected: 1
                },
                title: {
                    text: 'AAPL Stock Price'
                },
                series: [{
                    name: 'AAPL',
                    data: data,
                    tooltip: {
                        valueDecimals: 2
                    }
                }]
            });
            
        });

        $('#model-tabs').on('click', 'a[data-toggle="tab"]', function (e) {
            e.preventDefault();

            var $link = $(this);

            if (!$link.parent().hasClass('active')) {

                //remove active class from other tab-panes
                $('.tab-content:not(.' + $link.attr('href').replace('#', '') + ') .tab-pane').removeClass('active');

                // click first submenu tab for active section
                $('a[href="' + $link.attr('href') + '_all"][data-toggle="tab"]').click();

                // activate tab-pane for active section
                $('.tab-content.' + $link.attr('href').replace('#', '') + ' .tab-pane:first').addClass('active');
            }

        });
    }
});