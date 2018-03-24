﻿$(document).ready(function ($) {
	"use strict";
	if (localStorage.getItem("is_login") != 1) {
		window.location.href = "/login.html"
	}
	else {
		$('#init_msg_div').show();
		$('#init_msg').show();
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

		$('.dt_picker').datepicker({
			format: "M-yyyy",
			viewMode: "months",
			minViewMode: "months",
			autoclose: 'true'
		}).datepicker("setDate", new Date());

		$('.dt_picker').closest('div').find('.fa-calendar').click(function () {
			$(this).closest('div').find('.dt_picker').focus();
		});

		$('#ddl_indicator').change(function (e) {
			ChangeStrength();
		});

		$("#btnExcelExport").click(function () {
			if ($.ajaxQ.get_remaining_cnt() == 0) {
				var portoflio_dt_full = new Date("01-" + $('#portfolio_date').val());
				var limit = $('#ddl_limit').val();
				var indicator_type = $('#ddl_indicator').val();
				var strength = $('#txtstrength').val();
				var filename = "Top_" + limit + "_portfolios_by_" + (($('#ddl_indicator').val() == 'XF') ? 'fundamental' : ($('#ddl_indicator').val() == 'XT') ? "technical" : 'fundamental_and_technical') + ".xls";
				var worksheetname = "Top_" + limit + "_portfolios_by_" + $('#ddl_indicator').val();
				var html = $('.buy_sell_tbl').html()
				//$('.buy_sell_tbl').find('.text_buy_sell_status').remove();
				$(".buy_sell_tbl span.tkr-fullname").each(function () {
					return $(this).html(" (" + $(this).html() + ")");
				});
				$(".buy_sell_tbl").table2excel({
					filename: filename,
					worksheetName: worksheetname
				});

				$('.buy_sell_tbl').html(html);
			}
			else {
				alert("Please wait all data is downloaded.");
			}
		});

		$('#btnSimulate').click(function (e) {
			e.preventDefault();
			var portoflio_dt_full = new Date("01-" + $('#portfolio_date').val());
			var indicator_type = $('#ddl_indicator').val();
			var ddl_target = $('#ddl_target').val();
			ResetBuySellTBL();
			$.blockUI();
			BindMonthlyData(portoflio_dt_full, indicator_type, ddl_target);
		});

		function ResetBuySellTBL() {
			$.ajaxQ.abortAll();
			$('.portfolio-tkr-items').hide();
			$('#init_msg_div').show();
			$('#init_msg').hide();
			$('.buy_sell_tbl').empty();
			$('#_div_ticker_dtl').hide();
			$('.buy_sell_tbl').html('<thead><tr><th style="background-color: #e0dfdf;"><div class="status font-bold" style="margin-bottom: 28px;"><div class="status-title left" style="margin-top: 6px;">Tickers</div></div></th></tr></thead><tbody>');
		}

		function BindMonthlyData(portoflio_dt_full, indicator_type, target_type) {
			var portoflio_dt = moment(portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
			var settings = {
				"async": true,
				"crossDomain": true,
				"url": $.api_base_url + "/indicator_actual_value?date=" + portoflio_dt + "&indicator_type=" + indicator_type + "&target_type=" + target_type,
				"method": "POST",
				"contentType": 'application/json;charset=UTF-8',
				"headers": {
					"Content-Type": "application/json",
					"Authorization": "AD3EDSFEF3EF23E123",
				}
			}

			$.ajax(settings).done(function (response) {
				if (response != undefined || response != '') {
					var resp = jQuery.parseJSON(JSON.stringify(response));
					if (resp.status_code == 200) {
						var data = resp.data;
						var columnIndex = 0;
						var colcnt = 0
						var total_gain = 0;
						var jsonObj = [];
						var col = [];
						for (var key in data[0]) {
							if (col.indexOf(key) === -1 && key != "ticker_id" && key != "ticker_name" && key != "ticker_symbol" && key != "value_date") {
								col.push(key);
							}
						}
						for (var i = 0; i < col.length; i++) {
							$('.buy_sell_tbl thead tr').append('<th data-key="' + col[i] + '" ><div class="status font-14">	<div class="status-title text-center" style="text-transform:capitalize;">' + col[i].replace(/_/g, ' ') + '</div></div></th>');

						}
						$.each(data, function (key, value) {
							var i = 0;
							var tkrhtml = '<td class="tkr_' + value.ticker_id + '" data-ticker="' + value.ticker_id + '"><div class="left">' + value.ticker_symbol + ''
											+ '<span class="tkr-fullname">' + value.ticker_name + '</span>'
											+ '</div></td>'

							for (i = 0; i < col.length ; i++) {
								tkrhtml += '<td data-start="" data-end="">' + ((value[col[i]] != null) ? value[col[i]] : '') + '</td>'
							}

							$('.buy_sell_tbl tbody').append('<tr>' + tkrhtml + '</tr>')
						});
						$('#_div_ticker_dtl').show();
					}
				}
			}).always(function () {
				$.unblockUI()
			});
		}
	}
});