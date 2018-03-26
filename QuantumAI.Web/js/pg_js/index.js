$(document).ready(function ($) {

    "use strict";
    if (localStorage.getItem("is_login") == 0) {
        window.location.href = "/login.html"
    }
    else if (localStorage.getItem("is_login") == 2) {
    	window.location.href = "/portfolio.html";
    }
    else {
        $('.page').show()
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
        $('.recc_dt_picker').datepicker({
            format: 'dd-M-yyyy',
            autoclose: 'true'

        }).datepicker("setDate", new Date());;

        $(document).on('click.bs.radio', '.btn-radio > .btn', function (e) {
            $(this).siblings().removeClass('active');
            $(this).addClass('active');
        });
    }
});