
(function ($) {
	"use strict";

	localStorage.setItem("is_login", 0);
	$('.input100').each(function () {
		$(this).on('blur', function () {
			if ($(this).val().trim() != "") {
				$(this).addClass('has-val');
			}
			else {
				$(this).removeClass('has-val');
			}
		})
	})

	$('.validate-input .input100').each(function () {
		$(this).on('blur', function () {
			$('#_errmsg').hide();
			if (validate(this) == false) {
				showValidate(this);
			}
			else {
				$(this).parent().addClass('true-validate');
			}
		})
	})

	var input = $('.validate-input .input100');

	$('.validate-form').on('submit', function () {
		var check = true;
		$('#_errmsg').hide();
		for (var i = 0; i < input.length; i++) {
			if (validate(input[i]) == false) {
				showValidate(input[i]);
				check = false;
			}
		}
		if (check) {
			if ($('#_usrname').val() == 'admin' && $('#_usrpass').val() == 'admin') {
				$('#_errmsg').show();
				$('#_errmsg').addClass('alert-success');
				$('#_errmsg').removeClass('alert-danger');
				$('#_errmsg').html('<strong>Success!</strong> Welcome Admin.');
				localStorage.setItem("is_login", 1);
				window.location.href = "recommendation.html";
			}
			else if ($('#_usrname').val() == 'demouser' && $('#_usrpass').val() == 'demouser') {
				$('#_errmsg').show();
				$('#_errmsg').addClass('alert-success');
				$('#_errmsg').removeClass('alert-danger');
				$('#_errmsg').html('<strong>Success!</strong> Welcome User.');
				localStorage.setItem("is_login", 2);
				window.location.href = "recommendation.html";
			}
			else {
				$('#_errmsg').show();
				$('#_errmsg').removeClass('alert-success');
				$('#_errmsg').addClass('alert-danger');
				$('#_errmsg').html('<strong>Alert!</strong> Please enter valid username & password.');
			}
		}

		return false;
	});


	$('.validate-form .input100').each(function () {
		$(this).focus(function () {
			hideValidate(this);
			$(this).parent().removeClass('true-validate');
		});
	});

	function validate(input) {
		if ($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
			if ($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
				return false;
			}
		}
		else {
			if ($(input).val().trim() == '') {
				return false;
			}
		}
	}

	function showValidate(input) {
		var thisAlert = $(input).parent();

		$(thisAlert).addClass('alert-validate');
	}

	function hideValidate(input) {
		var thisAlert = $(input).parent();

		$(thisAlert).removeClass('alert-validate');
	}
})(jQuery);