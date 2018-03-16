$(document).ready(function ($) {

    "use strict";
    if (localStorage.getItem("is_login") != 1) {
        window.location.href = "/login.html"
    }
    else {
        $('.page').show();
        var $menu = $('#menu'),
               $menulink = $('.menu-link'),
               $menuTrigger = $('.has-submenu > a');

        $menulink.click(function (e) {
            e.preventDefault();
            $menulink.toggleClass('active');
            $menu.toggleClass('active');
        });

        $menuTrigger.click(function (e) {
            e.preventDefault();
            var $this = $(this);
            $this.toggleClass('active').next('ul').toggleClass('active');
        });
        $('#_div_ticker_dtl').show();
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

        $('#_div_ticker_dtl').hide();
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