$(document).ready(function ($) {

    "use strict";
    if (localStorage.getItem("is_login") != 1) {
        window.location.href = "/login.html"
    }
    else {
        $('.page').show();
    }
});