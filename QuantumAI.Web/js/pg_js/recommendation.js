var is_request_complete = 0;
var request_count = 0;
var inst;
var text = ["Request accepted by server", "Data validated", "Gathering Data", "Processing Request", "Calculating the Gains", "Creating Recommendations", "Your Recommendation is ready."];
var counter = 0;
var elem = document.getElementById("loader_msg");
var imgelem = document.getElementById("_loading_img");
var login_type = 0;
$(document).ready(function ($) {
	"use strict";
	if (localStorage.getItem("is_login") == null || localStorage.getItem("is_login") == 0) {
		window.location.href = "/login.html"
	}
	else {
		$('#menu').find('li[data-login-type="1"]').show();
		if (localStorage.getItem("is_login") == 2) {
			$('#menu').find('li[data-login-type="1"]').hide();
		}
		login_type = localStorage.getItem("is_login");
		$('#init_msg_div').show();
		$('#init_msg').show();
		$('.portfolio-tkr-items').hide();
		$('.page').show();
		ChangeStrength();
		var cur_dt = new Date();
		var lastdt = new Date((cur_dt.getFullYear()), cur_dt.getMonth(), 1)
		$('.dt_picker').datepicker({
			format: "M-yyyy",
			viewMode: "months",
			minViewMode: "months",
			autoclose: 'true',
			startDate: new Date('1998/01/01')
		}).datepicker("setDate", lastdt);


		$('.dt_picker').closest('div').find('.fa-calendar').click(function () {
			$(this).closest('div').find('.dt_picker').focus();
		});

		$('#ddl_indicator').change(function (e) {
			ChangeStrength();
		});

		$('#ddl_target').change(function (e) {
			ChangeStrength();
		});

		$('#ddl_adv_rule').change(function (e) {
			ChangeStrength();
		});

		$("#btnExcelExport").click(function () {
			if (is_request_complete == 1) {
				if ($.ajaxQ.get_remaining_cnt() == 0) {
					var portoflio_dt_full = moment("01-" + $('#portfolio_date').val(), "DD-MMM-YYYY").toDate();
					var limit = $('#ddl_limit').val();
					var indicator_type = $('#ddl_indicator').val();
					var target_type = $('#ddl_target').val();
					var strength = $('#txtstrength').val();
					var filename = "Top_" + limit + "_" + (($('#ddl_target').val() == "1") ? "BUY" : "SHORT/SELL") + "_recommendations_by_" + (($('#ddl_indicator').val() == 'XF') ? 'fundamental' : ($('#ddl_indicator').val() == 'XT') ? "technical" : 'fundamental_and_technical') + ".xls";
					var worksheetname = "Top_" + limit + "_" + (($('#ddl_target').val() == "1") ? "BUY" : "SHORT/SELL") + "_recommendations_by_" + $('#ddl_indicator').val();
					var html = $('.buy_sell_tbl').html()
					$('.buy_sell_tbl').find('.text_buy_sell_status').remove();
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
					alert("Please wait till all months data is downloaded.");
				}
			}
			else {
				alert("Please click on simulate button and then click on excel icon to download excel.");
			}
		});

		function ChangeStrength() {
			if ($('#ddl_indicator').val() == 'XF' || $('#ddl_indicator').val() == 'XS') {
				$("#txtstrength").removeAttr("disabled");

				$('#ddl_adv_rule').removeAttr("disabled");
				if ($('#ddl_adv_rule').val() == "0") {
					$('#txtstrength').val("-");
					$('#txtstrength').attr("disabled", "disabled");
					$('#spn_angle_sign').find('i').removeClass('fa-angle-left').addClass('fa-angle-right');
				} else {
					$('#txtstrength').removeAttr("disabled");
					if ($('#ddl_target').val() == "1") {
						$('#txtstrength').val("25");
						$('#spn_angle_sign').find('i').removeClass('fa-angle-left').addClass('fa-angle-right');
					} else {
						$('#txtstrength').val("0");
						$('#spn_angle_sign').find('i').removeClass('fa-angle-right').addClass('fa-angle-left');
					}
				}
			}
			else {
				$('#txtstrength').val("0");
				$('#txtstrength').attr("disabled", "disabled");
				$('#ddl_adv_rule').val("0");
				$('#ddl_adv_rule').attr("disabled", "disabled");

			}
		}

		$('#btnRecommend').click(function (e) {
			e.preventDefault();
			var portoflio_dt_full = moment("01-" + $('#portfolio_date').val(), "DD-MMM-YYYY").toDate();
			var limit = $('#ddl_limit').val();
			var indicator_type = $('#ddl_indicator').val();
			var target_type = $('#ddl_target').val();
			var strength = $('#txtstrength').val();
			var adv_rule = $('#ddl_adv_rule').val();
			if (strength == "-") {
				strength = "0";
			}
			ResetBuySellTBL();
			$.blockUI();
			inst = setInterval(change, 3000);

			var i = 0;
			for (i = 0; i < parseInt($("#ddl_no_of_month").val()) ; i++) {
				var dt = moment(portoflio_dt_full).add(i, 'M').toDate();
				if ($('.buy_sell_tbl thead').find('th.head_mon_' + dt.getMonth() + "_" + dt.getFullYear()) == undefined || $('.buy_sell_tbl thead').find('th.head_mon_' + dt.getMonth() + "_" + dt.getFullYear()).length == 0) {
					$('.buy_sell_tbl thead tr').append('<th class="head_mon_' + dt.getMonth() + "_" + dt.getFullYear() + '" data-month="' + dt.getMonth() + '" data-year="' + dt.getFullYear() + '"><div class="status font-14">	<div class="status-title text-center">' + moment(dt).format("MMM") + ' ' + dt.getFullYear() + '</div><div class="status-number"><div class="left _tkr_month_count"></div><div class="right _tkr_month_percent_gain"></div></div></div></th>');
				}
			}

			BindMonthlyData(portoflio_dt_full, indicator_type, target_type, strength, limit, adv_rule);
			
			//var inst2 = setInterval(executefor_othermnth.bind(null, portoflio_dt_full, indicator_type, target_type, strength, limit, adv_rule), 3000);

			//var inst3 = setInterval(CalculateTickerYrReturn.bind(null, target_type), 3000);
		//}
		});

		function CalculateYearlyReturns(totalreturn) {
			var current_total = parseFloat($('#total_yrl_rtn').html());
			if (current_total == null || current_total == undefined || current_total == '' || isNaN(current_total)) {
				current_total = 0;
			}

			var totalyrreturn = (current_total + totalreturn);
			if (isFinite(totalyrreturn)) {
				$('#total_yrl_rtn').removeClass('negative').removeClass('negative').addClass((totalyrreturn < 0) ? 'negative' : ((totalyrreturn > 0) ? 'positive':'')).html(totalyrreturn.toFixed(2));
			}
		}

		function ResetBuySellTBL() {
			$.ajaxQ.abortAll();
			$('.portfolio-tkr-items').hide();
			$('#init_msg_div').show();
			is_request_complete = 0;
			request_count = 0;
			$('#init_msg').hide();
			$('.top_monthbuysell-dtl').find('.bottom_tkr_header').html('Top 5 Months');
			$('#month_rtn_progress').attr('data-percentage', 10);
			$('#month_rtn_progress').find('.progress-value div').html("1 / " +  $("#ddl_no_of_month").val() + " M");
			$('.buy_sell_tbl').empty();
			$('.top_buysell-dtl .progress-info').empty();
			$('.bottom_buysell-dtl .progress-info').empty();
			$('#_tbl_previous_removed_tkr tbody').empty();
			$('#_tbl_newly_added_tkr tbody').empty();
			counter=0;
			if ($('#ddl_target').val() == "1") {
				$('.top_buysell-dtl').find('.top_tkr_header').html('Top 5 Buys');
				$('.bottom_buysell-dtl').find('.bottom_tkr_header').html('Bottom 5 Buys');
			}
			else {
				$('.top_buysell-dtl').find('.top_tkr_header').html('Top 5 Sells');
				$('.bottom_buysell-dtl').find('.bottom_tkr_header').html('Bottom 5 Sells');
			}
			$('.buy_sell_tbl').html('<thead><tr><th style="background-color: #e0dfdf;"><div class="status font-bold" style="margin-bottom: 28px;"><div class="status-title left" style="margin-top: 6px;">Top Tickers  <br>' + moment(new Date()).format('lll') + '</div><div class="status-number right"  style="font-size: 24px;"><span id="total_yrl_rtn"></span></div></div></th></tr></thead><tbody>');
		}


		function executefor_othermnth(portoflio_dt_full, indicator_type, target_type, strength, limit, adv_rule) {
			if (is_request_complete == 1) {
				var i = 1;
				//for (i = 1; i < parseInt($("#ddl_no_of_month").val()) ; i++) {
				var dt = moment(portoflio_dt_full).add(i, 'M').toDate();
				var max_date = moment("01-" + $('#portfolio_date').val(), "DD-MMM-YYYY").add(parseInt($("#ddl_no_of_month").val()), 'M').toDate();
				
				if (dt < max_date) {
					BindMonthlyData(dt, indicator_type, target_type, strength, limit, adv_rule);
				}
				else {
					CalculateTickerYrReturn(target_type);
				}
			//	}
				//clearInterval(inst2);

			}
		}

		function change() {
			var elem = document.getElementById("loader_msg");
			var imgelem = document.getElementById("_loading_img");

			if (elem != null && elem != undefined) {

				if (counter == (text.length - 1) && is_request_complete == 1) {
					if (counter <= text.length) {
						elem.innerHTML = text[counter];
					}
					counter++;
				}
				else if (counter < (text.length - 1) || counter == text.length) {
					if (counter <= text.length) {
						elem.innerHTML = text[counter];
					}
					counter++;
				}
				if (counter == text.length) {
					imgelem.src = "/images/loading-complete2.gif"
					clearInterval(inst);
					setTimeout(function () {
						$('#init_msg_div').hide();
						$('.portfolio-tkr-items').show();
						$.unblockUI()
					}, 2000);
				}
			}
		}

		function BindMonthlyData(portoflio_dt_full, indicator_type, target_type, strength, limit, adv_rule) {

			var portoflio_dt = moment(portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
			var form = new FormData();
			var settings = {
				"async": true,
				"crossDomain": true,
				"url": $.api_base_url + "/recommendation_predict_month?date=" + portoflio_dt + "&indicator_type=" + indicator_type + "&target_type=" + target_type + "&adv_weight=" + strength + "&limit=" + limit + "&adv_rule=" + adv_rule,
				"method": "GET",
				"headers": {
					"Content-Type": "application/json",
					"Authorization": "AD3EDSFEF3EF23E123",
				},
				"processData": false,
				"contentType": false,
				"mimeType": "multipart/form-data",
				"data": form
			}

			$.ajax(settings).done(function (response) {
				if (response != undefined || response != '') {
					var resp = jQuery.parseJSON(response);
					if (resp.status_code == 200) {
						var data = resp.data;
						var columnIndex = $('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + "_" + portoflio_dt_full.getFullYear()).index();

						var colcnt = 0
						var total_gain = 0;
						$.each(data, function (key, value) {
							total_gain = total_gain + ((value.fundamental_strength != null && value.fundamental_strength != '') ? value.fundamental_strength : 0);
							colcnt = colcnt + 1;
							if ($('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id) == undefined || $('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).length == 0) {

								var tkrhtml = '<td class="tkr_' + value.ticker_id + '" data-ticker="' + value.ticker_id + '"><div class="left" style="cursor: pointer;" onclick="BindTickerMonthlyData(\'' + portoflio_dt + '\',\'' + value.ticker_id + '\',\'' + $.trim(value.ticker_name.replace(/'/g, '\\\'')) + '\',\'' + $.trim(value.ticker_symbol.replace(/'/g, '\\\'')) + '\')"><span class="_trk_symbol">' + value.ticker_symbol + '</span>'
											+ '<span class="tkr-fullname">'  + value.ticker_name + '</span>'
											+ '</div><div class="right"><div class="right _tkr_yr_rtn"></div></td>'

								var i = 0;
								for (i = 0; i < ($(".buy_sell_tbl thead").find('tr')[0].cells.length - 1) ; i++) {
									tkrhtml += '<td data-start="" data-end=""></td>'
								}
								$('.buy_sell_tbl tbody').append('<tr>' + tkrhtml + '</tr>')
							}
							$('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).closest('tr').find('td').eq(columnIndex).attr('data-start', ((value.fundamental_strength != null) ? value.fundamental_strength : "")).attr('data-end', ((target_type == 1) ? ((value.pred_buy_fund_probability != null) ? ((value.pred_buy_fund_probability * 100).toFixed(2)) : '-') : ((target_type == 0) ? ((value.pred_short_sell_fund_probability != null) ? ((value.pred_short_sell_fund_probability * 100).toFixed(2)) : '-') : ''))).addClass((value.fundamental_strength > 0) ? 'buy' : ((value.fundamental_strength < 0) ? 'sell' : '')).html('<div class="clearfix"><div class="left">' + ((value.fundamental_strength != null) ? ((value.fundamental_strength).toFixed(2)) : '-') + '</div><div class="right">' + ((target_type == 1) ? ((value.pred_buy_fund_probability != null) ? ((value.pred_buy_fund_probability * 100).toFixed(2) + "%") : '-') : ((target_type == 0) ? ((value.pred_short_sell_fund_probability != null) ? ((value.pred_short_sell_fund_probability * 100).toFixed(2) + "%") : '-') : '-')) + '</div></div><div class="left" style="margin-left: -11.75px;">' + ((target_type == 1) ? '<div class="sim_text_buy_sell_status buy">B</div>' : ((target_type == 0) ? '<div class="sim_text_buy_sell_status sell">S</div>' : '<div class="sim_text_buy_sell_status">-</div>')) + ((moment(value.value_date).toDate()<=new Date())?((value.pred_tech_target == 1) ? '<div class="sim_text_buy_sell_status buy">B</div>' : ((value.pred_tech_target == 0) ? '<div class="sim_text_buy_sell_status sell">S</div>' : '<div class="sim_text_buy_sell_status">-</div>')): '') + '</div>');
						});

						if (total_gain != 0) {
							total_gain = total_gain / colcnt;
							$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_percent_gain').addClass((total_gain < 0) ? 'negative' : '').html(total_gain.toFixed(2))
							$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_count').html(colcnt + " " + ((target_type == 1) ? "Buys" : "Shorts/Sells"));
						} else {
							$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_percent_gain').html('-')
							$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_count').html(colcnt + " " + ((target_type == 1) ? "Buys" : "Shorts/Sells"));;

						}

						counter = text.length - 1;
						if (is_request_complete == 0) {
							change();
							var last_mn_dt = moment(portoflio_dt_full).add(-1, 'M').toDate();

							BindLastMonthRemovedData(last_mn_dt, indicator_type, target_type, strength, limit, adv_rule, data);

							is_request_complete = 1;
						}
						else {
							ShowMonthReturnProgress();
						}
						executefor_othermnth(portoflio_dt_full, indicator_type, target_type, strength, limit, adv_rule);
						is_request_complete = 1;
						request_count = request_count + 1;
						//CalculateYearlyReturns(total_gain);
						CalculateMonthlyReturn();
						//CalculateTickerYrReturn(target_type);
					}
				}
			});
		}

		function BindLastMonthRemovedData(portoflio_dt_full, indicator_type, target_type, strength, limit, adv_rule, current_mnth_data) {

			var portoflio_dt = moment(portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
			var form = new FormData();
			var settings = {
				"async": true,
				"crossDomain": true,
				"url": $.api_base_url + "/recommendation_predict_month?date=" + portoflio_dt + "&indicator_type=" + indicator_type + "&target_type=" + target_type + "&adv_weight=" + strength + "&limit=" + limit + "&adv_rule=" + adv_rule,
				"method": "GET",
				"headers": {
					"Content-Type": "application/json",
					"Authorization": "AD3EDSFEF3EF23E123",
				},
				"processData": false,
				"contentType": false,
				"mimeType": "multipart/form-data",
				"data": form
			}

			$.ajax(settings).done(function (response) {
				if (response != undefined || response != '') {
					var resp = jQuery.parseJSON(response);
					if (resp.status_code == 200) {
						var data = resp.data;
						$.each(data, function (key, value) {
							if ($('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id) == undefined || $('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).length == 0) {
								$('#_tbl_previous_removed_tkr tbody').append('<tr><td><div style="cursor: pointer;" onclick="BindTickerMonthlyData(\'' + portoflio_dt + '\',\'' + value.ticker_id + '\',\'' + $.trim(value.ticker_name.replace(/'/g, '\\\'')) + '\',\'' + $.trim(value.ticker_symbol.replace(/'/g, '\\\'')) + '\')">' + value.ticker_symbol + '<span class="tkr-fullname">' + value.ticker_name + '</span></td><td style="width: 120px;"><span class="tkr-cp">' + ((value.fundamental_strength != null) ? ((value.fundamental_strength).toFixed(2)) : '-') + '</span><span class="tkr-cprct" style="font-weight: 500;color: #989898;">' + ((value.next_month_fundamental_strength != null) ? ((value.next_month_fundamental_strength).toFixed(2)) : '-') + '</span></div></td></tr>');
							}
						});
						$.each(current_mnth_data, function (key, value) {
							var result = false;
							$.each(data, function (key2, item) {
								if (item.ticker_id == value.ticker_id) {
									result = true;
								}
							});

							if (!result) {
								$('#_tbl_newly_added_tkr tbody').append('<tr><td><div style="cursor: pointer;" onclick="BindTickerMonthlyData(\'' + portoflio_dt + '\',\'' + value.ticker_id + '\',\'' + $.trim(value.ticker_name.replace(/'/g, '\\\'')) + '\',\'' + $.trim(value.ticker_symbol.replace(/'/g, '\\\'')) + '\')">' + value.ticker_symbol + '<span class="tkr-fullname">' + value.ticker_name + '</span></td><td style="width: 120px;"><span class="tkr-cp">' + ((value.fundamental_strength != null) ? ((value.fundamental_strength).toFixed(2)) : '-') + '</span><span class="tkr-cprct" style="font-weight: 500;color: #989898;">' + ((value.last_month_fundamental_strength != null) ? ((value.last_month_fundamental_strength).toFixed(2)) : '-') + '</span></div></td></tr>');
							}
						});

					}
				}

				if ($('#_tbl_previous_removed_tkr tbody').html().trim() == '') {
					$('#_tbl_previous_removed_tkr tbody').html("<tr><td colspan='2'>No Tickers previously removed.</td></tr>")
				}

				if ($('#_tbl_newly_added_tkr tbody').html().trim() == '') {
					$('#_tbl_newly_added_tkr tbody').html("<tr><td colspan='2'>No Tickers newly added.</td></tr>")
				}
			});

		}

		function CalculateMonthlyReturn() {
			var MjsonObj = [];
			$('.buy_sell_tbl thead th:not(:first)').each(function () {
				var item = {}
				item["month"] = $(this).find('.status-title').html();
				item["percent_gain"] = (isNaN(parseFloat($(this).find('._tkr_month_percent_gain').html()))) ? 0 : parseFloat($(this).find('._tkr_month_percent_gain').html());
				MjsonObj.push(item);
			});
			MjsonObj = MjsonObj.sort(function (a, b) {
				var x = a.percent_gain < b.percent_gain ? -1 : 1;
				return x;
			});
			var month = $(this).attr('data-month');
			var yr = $(this).attr('data-year');
			$('.top_monthbuysell-dtl .monthly_returns').empty();
			$.each(MjsonObj.slice(-5).reverse(), function (key, value) {
				$('.top_monthbuysell-dtl .monthly_returns').append('<div class="status font-14 tkr_tb_' + month + '_' + yr + '">	<div class="status-title left">' + value.month + '</div><div class="status-number right tkr_total_gain"> ' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) ) : '') + ' </div></div>');
			});
			
		}

		function ShowMonthReturnProgress() {
			$('.top_monthbuysell-dtl').find('.bottom_tkr_header').html('Monthly Recommendation in progress ...');
			if (is_request_complete == 1) {
				var perct = parseInt(Math.ceil((((request_count) / parseInt($("#ddl_no_of_month").val())) * 100) / 10.0)) * 10
				if (perct == 100) {
					$('.top_monthbuysell-dtl').find('.bottom_tkr_header').html('Top 5 Months');
				}
				$('#month_rtn_progress').attr('data-percentage', perct);
				$('#month_rtn_progress').find('.progress-value div').html(((request_count) +1	) + " / " + parseInt($("#ddl_no_of_month").val()) + " M");
			}
		}
	}
});

function BindTickerMonthlyData(portfolio_date, ticker_id, ticker_name, ticker_symbol) {
	if (login_type == 1) {
		$('._ticker_buy_sell_tbl').html('<thead><tr><th style="background-color: #e0dfdf;"><div class="status font-bold" style="margin-bottom: 28px;"><div class="status-title left" style="margin-top: 6px;">Ticker Monthly % Returns</div></div></th></tr></thead><tbody>');

		$.blockUI();
		var portoflio_from_dt = moment(portfolio_date).format("YYYY-MM-DD HH:mm:ss");
		var to_portoflio_dt_full = moment(portfolio_date).add((parseInt($("#ddl_no_of_month").val()) - 1), 'M').toDate();
		to_portoflio_dt_full = new Date(to_portoflio_dt_full.getFullYear(), to_portoflio_dt_full.getMonth() + 1, 0);
		$('#modal_graph .modal-title').html(ticker_name + "<small> (" + ticker_symbol + ")</small>")
		var portoflio_to_dt = moment(to_portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
		var settings = {
			"async": true,
			"crossDomain": true,
			"url": $.api_base_url + "/simulation_actual_data_month?from_date=" + portoflio_from_dt + "&limit=" + parseInt($("#ddl_no_of_month").val()) + "&ticker_id=" + ticker_id,
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
					var dat = resp.data;
					var columnIndex = 0;
					var colcnt = 0
					var total_gain = 0;
					var jsonObj = [];
					var col = [];
					for (var key in dat[0]) {
						if (col.indexOf(key) === -1 && key != "value_date") {
							col.push(key);
						}
					}
					for (var i = 0; i < col.length; i++) {
						if (col[i].indexOf("_value") == -1) {
							$('._ticker_buy_sell_tbl thead tr').append('<th data-key="' + col[i] + '" ' + ' ><div class="status font-14">	<div class="status-title text-center" style="text-transform:capitalize;">' + col[i].replace("USD_M", "<br>USD (M) ").replace(/_/g, ' ') + '</div></div></th>');
						}

					}
					$.each(dat, function (key, value) {
						var i = 0;
						var tkrhtml = '<td><div class="left">' + value.value_date + '</div></td>'

						for (i = 0; i < col.length ; i++) {
							if (col[i].indexOf("_value") == -1) {
								if (col[i].indexOf("_mean") >= 0) {
									var col_name = (col[i].split('_mean')[0]).split('analyst_estimate_')[1]
									var data = value[col_name + "_value"]
									//var data2 = dat[((key>0)?(key - 1):0)][col_name + "_value"]
									//if (data2 != undefined) 
									{
										var col_value = value[col[i]]
										if (data != undefined) {
											if (data != col_value) {
												col_value = ((value.value_date == 'Acc/Dcc') ? ((parseFloat(value[col[i]])).toFixed(2) + '%') : (parseFloat(value[col[i]])).toFixed(4)) + ' <div class="right "><small style="color:#007bff;">' + ((value.value_date == 'Acc/Dcc') ? ((parseFloat(data)).toFixed(2) + '%') : (parseFloat(data)).toFixed(4)) + "</small></div>";
											}
											else {
												col_value = ((value.value_date == 'Acc/Dcc') ? ((parseFloat(value[col[i]])).toFixed(2) + '%') : (parseFloat(value[col[i]])).toFixed(4));
											}
										} else {
											col_value = ((value.value_date == 'Acc/Dcc') ? ((parseFloat(value[col[i]])).toFixed(2) + '%') : (parseFloat(value[col[i]])).toFixed(4));
										}

										tkrhtml += '<td style="padding: .5rem;font-size: 14px;" data-start="" data-end="">' + ((value[col[i]] != null) ? col_value : '-') + '</td>'
									}
								} else {
									tkrhtml += '<td style="padding: .5rem;font-size: 14px;" data-start="" data-end="">' + ((value[col[i]] != null) ? ((value.value_date == 'Acc/Dcc') ? ((parseFloat(value[col[i]])).toFixed(2) + '%') : (parseFloat(value[col[i]])).toFixed(4)) : '-') + '</td>'
								}
							}
						}

						$('._ticker_buy_sell_tbl tbody').append('<tr ' + ((value.value_date == 'Acc/Dcc') ? 'class="highlight"' : '') + '>' + tkrhtml + '</tr>')
					});
				}

				$('#lnkTickerMntRtn').click();
			}
		}).always(function () {
			$.unblockUI()
		});
	}
}



function CalculateTickerYrReturn(target_type) {
	//if ($.ajaxQ.get_remaining_cnt() == 0) {
	var jsonObj = [];
	$('.buy_sell_tbl tbody tr').each(function () {
		var yr_return = 0; var start_close_price = null; var end_close_price = null; var i = 0; var start_cnt = 0; var end_cnt = 0;
		var tdlength = $(this).find('td').not(':first').length;
		var ticker_id = $(this).find('td:first').attr('data-ticker');
		$(this).find('td').not(':first').each(function (index, ele) {
			i++;
			var tr_start_close_price = parseFloat($(this).attr('data-start'));

			start_cnt++;
			if (tr_start_close_price == null || tr_start_close_price == undefined || tr_start_close_price == '' || isNaN(tr_start_close_price)) {
				tr_start_close_price = null;
				start_cnt = start_cnt - 1;
			}

			var tr_end_close_price = parseFloat($(this).attr('data-end'));
			end_cnt++;
			if (tr_end_close_price == null || tr_end_close_price == undefined || tr_end_close_price == '' || isNaN(tr_end_close_price)) {
				tr_end_close_price = null;
				i = i - 1;
				end_cnt = end_cnt - 1;
			}

			if (tr_start_close_price != null && start_close_price == null) {
				start_close_price = tr_start_close_price;
			}
			else {
				start_close_price = start_close_price + tr_start_close_price;
			}
			if (tr_end_close_price != null && end_close_price == null) {
				end_close_price = tr_end_close_price;
			} else {
				end_close_price = end_close_price + tr_end_close_price;
			}

		});

		start_close_price = start_close_price / start_cnt;
		end_close_price = end_close_price / end_cnt;
		if (isFinite(yr_return)) {
			$(this).find('td:first-child').find('._tkr_yr_rtn').removeClass('negative').addClass((yr_return < 0) ? 'negative' : '').html(((start_close_price < 0) ? ("(" + start_close_price.toFixed(2) + ")") : start_close_price.toFixed(2)) + "/" + end_close_price.toFixed(2) + "%");
			var item = {}
			item["ticker_id"] = ticker_id;
			item["ticker_symbol"] = $(this).find('td:first-child').find('._trk_symbol').html();
			item["ticker_name"] = $(this).find('td:first-child').find('.tkr-fullname').html();
			item["fundamental_strength"] = start_close_price;
			item["fundamental_prob"] = end_close_price;
			jsonObj.push(item);
		}
	});
	if (jsonObj != null && jsonObj.length > 0) {
		jsonObj = jsonObj.sort(function (a, b) {
			var x = a.fundamental_strength < b.fundamental_strength ? -1 : 1;
			return x;
		});
		$('.bottom_buysell-dtl .progress-info').empty();
		$('.top_buysell-dtl .progress-info').empty();
		$.each(jsonObj.slice(0, 5), function (key, value) {
			$('.bottom_buysell-dtl .progress-info').append('<div class="status font-14 tkr_tb_' + value.ticker_id + '">	<div class="status-title left">' + value.ticker_symbol + '</div><div class="status-number right tkr_total_gain"> ' + ((value.fundamental_strength != null) ? ((value.fundamental_strength).toFixed(2) + "/" + value.fundamental_prob.toFixed(2) + "%") : '') + ' </div></div>');
		});
		$.each(jsonObj.slice(-5).reverse(), function (key, value) {
			$('.top_buysell-dtl .progress-info').append('<div class="status font-14 tkr_tb_' + value.ticker_id + '">	<div class="status-title left">' + value.ticker_symbol + '</div><div class="status-number right tkr_total_gain"> ' + ((value.fundamental_strength != null) ? ((value.fundamental_strength).toFixed(2) + "/" + value.fundamental_prob.toFixed(2) + "%") : '') + ' </div></div>');
		});
	}
}
