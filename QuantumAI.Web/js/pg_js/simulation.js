var is_request_complete = 0;
var inst;
var text = ["Request accepted by server", "Data validated", "Gathering Data", "Processing Request", "Calculating the Gains", "Creating Portfolio", "Your Portfolio is ready."];
var counter = 0;
var elem = document.getElementById("loader_msg");
var imgelem = document.getElementById("_loading_img");
var config = {
	'.chosen-select': {},
	'.chosen-select-deselect': { allow_single_deselect: true },
	'.chosen-select-no-single': { disable_search_threshold: 10 },
	'.chosen-select-no-results': { no_results_text: 'Oops, nothing found!' },
	'.chosen-select-rtl': { rtl: true },
	'.chosen-select-width': { width: '95%' }
}
var login_type = 0;

$(document).ready(function ($) {

	"use strict";
	if (localStorage.getItem("is_login")==null || localStorage.getItem("is_login") == 0) {
		window.location.href = "/login.html"
	}
	else {
		$('#menu').find('li[data-login-type="1"]').show();
		if (localStorage.getItem("is_login") == 2) {
			$('#menu').find('li[data-login-type="1"]').hide();
		}
		login_type = localStorage.getItem("is_login");

		$.blockUI();
		$('#init_msg_div').show();
		$('#init_msg').show();
		FillTicker_DropDown();
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

		var cur_dt = new Date();
		var lastdt = new Date((cur_dt.getFullYear()), cur_dt.getMonth(),1)
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

		$('#tickers-multiple').chosen({
			min_length: 2,
			no_results_text: 'No tickers found matching the above search text.'
		});

		$('#MyModal').on('hidden.bs.modal', function () {
			$('#tickerCsvUpload').val("");
			$('#chkCsvContainHeader').prop('checked', false);
		});

		$('#ddl_indicator').change(function (e) {
			ChangeStrength();
		});

		$("#btnExcelExport").click(function () {
			if ($.ajaxQ.get_remaining_cnt() == 0) {
				if ($.fn.DataTable.isDataTable('#buy_sell_tbl')) {
						$('#buy_sell_tbl').DataTable().destroy();
					}

				var portoflio_dt_full = moment("01-" + $('#portfolio_date').val(), 'DD-MMM-YYYY').toDate();
				var limit = $('#ddl_limit').val();
				var indicator_type = $('#ddl_indicator').val();
				var strength = $('#txtstrength').val();
				var filename = "Top_" + limit + "_simulations_by_" + (($('#ddl_indicator').val() == 'XF') ? 'fundamental' : ($('#ddl_indicator').val() == 'XT') ? "technical" : 'fundamental_and_technical') + ".xls";
				var worksheetname = "Top_" + limit + "_simulations_by_" + $('#ddl_indicator').val();
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
				
					$('#buy_sell_tbl').DataTable({
						"paging": false,
						"ordering": false,
						"info": false,
						"searching": false,
						scrollY: "500px",
						scrollX: true,
						scrollCollapse: true,
						fixedColumns: {
							leftColumns: 1
						}
					});
			}
			else {
				alert("Please wait till all months data is downloaded.");
			}
		});

		$('#btnSimulate').click(function (e) {
			e.preventDefault();
			var portoflio_dt_full = moment("01-" + $('#portfolio_date').val(), 'DD-MMM-YYYY').toDate();
			var limit = $('#ddl_limit').val();
			var indicator_type = $('#ddl_indicator').val();
			var ticker_id = $('#tickers-multiple').val();
			var strength = $('#txtstrength').val();
			var adv_rule = $('#ddl_adv_rule').val();

			ResetBuySellTBL();
			$.blockUI();
			//inst = setInterval(change, 3000);

			var i = 0;
			for (i = 0; i < parseInt($("#ddl_no_of_month").val()) ; i++) {
				var dt = moment(portoflio_dt_full).add(i, 'M').toDate();
				if ($('.buy_sell_tbl thead').find('th.head_mon_' + dt.getMonth() + "_" + dt.getFullYear()) == undefined || $('.buy_sell_tbl thead').find('th.head_mon_' + dt.getMonth() + "_" + dt.getFullYear()).length == 0) {
					$('.buy_sell_tbl thead tr').append('<th class="head_mon_' + dt.getMonth() + "_" + dt.getFullYear() + '" data-month="' + dt.getMonth() + '" data-year="' + dt.getFullYear() + '"><div class="status font-14">	<div class="status-title text-center">' + moment(dt).format("MMM") + ' ' + dt.getFullYear() + '</div><div class="status-number"><div class="left _tkr_month_count"></div><div class="right _tkr_month_percent_gain"></div></div></div></th>');
				}
			}
			var to_portoflio_dt_full = moment(portoflio_dt_full).add((parseInt($("#ddl_no_of_month").val())-1), 'M').toDate();
			to_portoflio_dt_full = new Date(to_portoflio_dt_full.getFullYear(), to_portoflio_dt_full.getMonth() + 1, 0);
			BindMonthlyData(portoflio_dt_full, to_portoflio_dt_full, indicator_type, ticker_id, strength, limit, adv_rule);

		});

		function ChangeStrength() {
			if ($('#ddl_indicator').val() == 'XF' || $('#ddl_indicator').val() == 'XS') {
				$("#txtstrength").removeAttr("disabled");
				$('#ddl_adv_rule').val("0");
				$('#ddl_adv_rule').removeAttr("disabled");
			}
			else {
				$('#txtstrength').val("0");
				$('#txtstrength').attr("disabled", "disabled");
				$('#ddl_adv_rule').val("0");
				$('#ddl_adv_rule').attr("disabled", "disabled");
			}
		}

		$("#btnuploadcsv").bind("click", function () {
			var regex = /^([a-zA-Z0-9\s_\\.\-:])+(.csv|.txt)$/;
			if (regex.test($("#tickerCsvUpload").val().toLowerCase())) {
				var jsonObj = [];
				var startindex = 0;
				if ($('#chkCsvContainHeader').is(":checked")) {
					startindex = 1;
				}
				if (typeof (FileReader) != "undefined") {
					var reader = new FileReader();
					reader.onload = function (e) {
						var rows = e.target.result.split("\n");
						for (var i = startindex; i < rows.length; i++) {
							var cells = rows[i].split(",");
							if (cells[0] != '') {
								$('#tickers-multiple option').each(function () {
									var symbol = $(this).attr('data-symbol');
									if ($.trim(symbol.toLowerCase()) === $.trim(cells[0].toLowerCase()) || $.trim(symbol.split('.')[0].toLowerCase()) === $.trim(cells[0].toLowerCase())) {
										jsonObj.push(this.value);
									}
								});
							}
						}

						$('#tickers-multiple').val(jsonObj);
						$('#tickers-multiple').trigger("chosen:updated");
						$('#lnkOpenCSVUploadModal').click();
					}
					reader.readAsText($("#tickerCsvUpload")[0].files[0]);
				}
			} else {
				alert("Please upload a valid CSV file.");
			}
		});

		function ResetBuySellTBL() {
			$.ajaxQ.abortAll();
			$('.portfolio-tkr-items').hide();
			$('#init_msg_div').show();
			is_request_complete = 0;
			$('#init_msg').hide();
			$('.top_monthbuysell-dtl').find('.bottom_tkr_header').html('Top 5 Gain Months');
			$('#month_rtn_progress').attr('data-percentage', 10);
			$('#month_rtn_progress').find('.progress-value div').html("1 / " + $("#ddl_no_of_month").val() + " M");
			if ($.fn.DataTable.isDataTable('.buy_sell_tbl')) {
				$('.buy_sell_tbl').DataTable().destroy();
			}
			$('.buy_sell_tbl').empty();
			$('#_div_ticker_dtl').hide();
			$('.top_buysell-dtl .progress-info').empty();
			$('.bottom_buysell-dtl .progress-info').empty();
			counter = 0;

			$('.buy_sell_tbl').html('<thead><tr><th style="background-color: #e0dfdf;"><div class="status font-bold" style="margin-bottom: 28px;"><div class="status-title left" style="margin-top: 6px;">' + $("#ddl_no_of_month").val() + 'M % Returns  <br>' + moment(new Date()).format('lll') + '</div><div class="status-number right"  style="font-size: 24px;"><span id="total_yrl_rtn"></span>%</div></div></th></tr></thead><tbody>');
		}

		function BindMonthlyData(from_portoflio_dt_full, to_portoflio_dt_full, indicator_type, ticker_id, strength, limit, adv_rule) {
			var from_portoflio_dt = moment(from_portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
			var to_portoflio_dt = moment(to_portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
			var data = { "from_date": from_portoflio_dt, "to_date": to_portoflio_dt, "indicator_type": indicator_type, "ticker_id": ticker_id, "adv_weight": strength, "limit": limit, "adv_rule": adv_rule }
			var settings = {
				"async": true,
				"crossDomain": true,
				"url": $.api_base_url + "/simulation_predict_month",
				"method": "POST",
				"data": JSON.stringify(data),
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

						$.each(data, function (key, value) {
							var portoflio_dt_full = moment(value.value_date, 'DD-MMM-YYYY').toDate();
							var columnIndex = $('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + "_" + portoflio_dt_full.getFullYear()).index();
							if ($('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id) == undefined || $('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).length == 0) {

								var tkrhtml = '<td class="tkr_' + value.ticker_id + '" data-ticker="' + value.ticker_id + '"><div class="left" style="cursor: pointer;" onclick="BindTickerMonthlyData(\'' + from_portoflio_dt + '\',\'' + to_portoflio_dt + '\',\'' + value.ticker_id + '\',\'' + $.trim(value.ticker_name.replace(/'/g, '\\\'')) + '\',\'' +  $.trim(value.ticker_symbol.replace(/'/g, '\\\'')) + '\')">' + value.ticker_symbol
											+ '<span class="tkr-fullname">' + value.ticker_name + '</span>'
											+ '</div><div class="right"><div class="right _tkr_yr_rtn"></div></td>'

								var i = 0;
								for (i = 0; i < ($(".buy_sell_tbl thead").find('tr')[0].cells.length - 1) ; i++) {
									tkrhtml += '<td data-start="" data-end=""></td>'
								}
								$('.buy_sell_tbl tbody').append('<tr>' + tkrhtml + '</tr>')
							}
							$('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).closest('tr').find('td').eq(columnIndex).attr('data-start', ((value.f_close_price != null) ? value.f_close_price : "")).attr('data-end', ((value.l_close_price != null) ? value.l_close_price : "")).addClass((value.percent_gain > 0) ? 'buy' : ((value.percent_gain < 0) ? 'sell' : '')).html('<div class="clearfix"><div class="left">' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) + "%") : '-') + '</div></div><div class="" style="margin-left: -11.75px;">' + ((value.pred_buy_fund_target == 1) ? '<div class="sim_text_buy_sell_status buy">B</div>' : ((value.pred_short_sell_fund_target == 1) ? '<div class="sim_text_buy_sell_status sell">S</div>' : ((value.pred_short_sell_fund_target == 0 || value.pred_buy_fund_target == 0) ? '<div class="sim_text_buy_sell_status">N</div>' : '<div class="sim_text_buy_sell_status">-</div>'))) + ((value.pred_xm_buy_fund_target == 1) ? '<div class="sim_text_buy_sell_status buy">B</div>' : ((value.pred_xm_short_sell_fund_target == 1) ? '<div class="sim_text_buy_sell_status sell">S</div>' : ((value.pred_xm_short_sell_fund_target == 0 || value.pred_xmo_buy_fund_target == 0) ? '<div class="sim_text_buy_sell_status">N</div>' : '<div class="sim_text_buy_sell_status">-</div>'))) + '<div class="" style="margin-left: 20px; display: inline-block;">' + ((value.pred_fundamental_strength == 1) ? '<div class="sim_text_buy_sell_status buy">B</div>' : ((value.pred_fundamental_strength == 2) ? '<div class="sim_text_buy_sell_status sell">S</div>' : '<div class="sim_text_buy_sell_status">N</div>')) + ' </div><div class="" style="margin-left: 20px; display: inline-block;">' + ((value.pred_tech_target == 1) ? '<div class="sim_text_buy_sell_status buy">B</div>' : ((value.pred_tech_target == 0) ? '<div class="sim_text_buy_sell_status sell">S</div>' : '<div class="sim_text_buy_sell_status">-</div>')) + "</div></div>");
							if (value.percent_gain != null && value.percent_gain != '') {
								total_gain = parseFloat($('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_percent_gain').attr('data-sum'));
								colcnt = parseInt($('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_percent_gain').attr('data-colcnt'));
								if (isNaN(total_gain)) {
									total_gain = 0;
								}
								if (isNaN(colcnt)) {
									colcnt = 0;
								}
								colcnt = colcnt + 1;

								total_gain = total_gain + value.percent_gain;
								$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_percent_gain').addClass((total_gain < 0) ? 'negative' : '').html(total_gain.toFixed(2) + '%').attr('data-sum', total_gain).attr('data-colcnt', colcnt);
								$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_count').html(colcnt);
							}

							if (isFinite(value.percent_gain)) {
								var exist = false;
								for (var index = 0; index < jsonObj.length; ++index) {

									var item = jsonObj[index];

									if (item.ticker_id == value.ticker_id) {
										exist = true;
										item.percent_gain = (item.percent_gain + value.percent_gain);
										break;
									}
								}
								if (!exist) {
									var item = {}
									item["ticker_id"] = value.ticker_id;
									item["ticker_symbol"] = value.ticker_symbol;
									item["percent_gain"] = value.percent_gain;
									jsonObj.push(item);
								}
							}
						});
						if (jsonObj != null && jsonObj.length > 0) {
							jsonObj = jsonObj.sort(function (a, b) {
								var x = a.percent_gain < b.percent_gain ? -1 : 1;
								return x;
							});
							for (var index = 0; index < jsonObj.length; ++index) {
								if (jsonObj[index].percent_gain != null && jsonObj[index].percent_gain != undefined) {
									$('.buy_sell_tbl tbody').find('td.tkr_' + jsonObj[index].ticker_id).find('._tkr_yr_rtn').html(jsonObj[index].percent_gain.toFixed(2) + '%');
								}
							}
							$('.bottom_buysell-dtl .progress-info').empty();
							$('.top_buysell-dtl .progress-info').empty();
							$.each(jsonObj.slice(0, 5), function (key, value) {
								$('.bottom_buysell-dtl .progress-info').append('<div class="status font-14 tkr_tb_' + value.ticker_id + '">	<div class="status-title left">' + value.ticker_symbol + '</div><div class="status-number right tkr_total_gain"> ' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) + "%") : '') + ' </div></div>');
							});
							$.each(jsonObj.slice(-5).reverse(), function (key, value) {
								$('.top_buysell-dtl .progress-info').append('<div class="status font-14 tkr_tb_' + value.ticker_id + '">	<div class="status-title left">' + value.ticker_symbol + '</div><div class="status-number right tkr_total_gain"> ' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) + "%") : '') + ' </div></div>');
							});
						}
						var month_total_gain = 0
						$('.buy_sell_tbl thead th ._tkr_month_percent_gain').each(function (index, ele) {
							var cnt = parseInt($(this).closest('th').find('._tkr_month_count').html());
							var cmonth_total_gain = parseFloat($(this).attr('data-sum'));

							if (isNaN(cmonth_total_gain)) {
								cmonth_total_gain = 0;
							}
							if (isNaN(cnt)) {
								cnt = 1;
							}

							cmonth_total_gain = cmonth_total_gain / cnt;
							$(this).attr('data-sum', cmonth_total_gain).html(cmonth_total_gain.toFixed(2));
							month_total_gain = month_total_gain + cmonth_total_gain;
						});


						$('#total_yrl_rtn').html(month_total_gain.toFixed(2));
						CalculateMonthlyReturn();
						

						$('#_div_ticker_dtl').show();
						$('.buy_sell_tbl').DataTable({
							"paging":   false,
							"ordering": false,
							"info": false,
							"searching": false,
							scrollY: "500px",
							scrollX: true,
							scrollCollapse: true,
							fixedColumns: {
								leftColumns: 1
							}
						});
					}
				}
			}).always(function () {
				$.unblockUI()
			});
		}

		function FillTicker_DropDown() {
			$('#tickers-multiple').empty();
			var settings = {
				"async": true,
				"crossDomain": true,
				"url": $.api_base_url + "/ticker",
				"method": "GET",
				"headers": {
					"Content-Type": "application/json",
					"Authorization": "AD3EDSFEF3EF23E123",
				},
				"processData": false,
				"contentType": false,
				"mimeType": "multipart/form-data"
			}
			$.ajax(settings).done(function (response) {
				if (response != undefined || response != '') {
					var resp = jQuery.parseJSON(response);
					if (resp.status_code == 200) {
						var data = resp.data;
						$.each(data, function (key, value) {
							$('#tickers-multiple').append("<option value='" + value["ticker_id"] + "' data-symbol='" + value["ticker_symbol"] + "'>" + value["ticker_name"] + "(" + value["ticker_symbol"] + ")" + "</option>")
						});
					}

					$('#tickers-multiple').trigger("chosen:updated");
				}
			}).always(function () {
				$.unblockUI();
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
				$('.top_monthbuysell-dtl .monthly_returns').append('<div class="status font-14 tkr_tb_' + month + '_' + yr + '">	<div class="status-title left">' + value.month + '</div><div class="status-number right tkr_total_gain"> ' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) + "%") : '') + ' </div></div>');
			});


		}

	}
});


function BindTickerMonthlyData(from_date, to_date, ticker_id, ticker_name, ticker_symbol) {
	if (login_type == 1) {
		$('._ticker_buy_sell_tbl').html('<thead><tr><th style="background-color: #e0dfdf;"><div class="status font-bold" style="margin-bottom: 28px;"><div class="status-title left" style="margin-top: 6px;">Ticker Monthly % Returns</div></div></th></tr></thead><tbody>');
		$('#modal_graph .modal-title').html(ticker_name + "<small> (" + ticker_symbol + ")</small>")

		$.blockUI();
		var portoflio_from_dt = moment(from_date).format("YYYY-MM-DD HH:mm:ss");
		var portoflio_to_dt = moment(to_date).format("YYYY-MM-DD HH:mm:ss");
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
							$('._ticker_buy_sell_tbl thead tr').append('<th data-key="' + col[i] + '" ' +  ' ><div class="status font-14">	<div class="status-title text-center" style="text-transform:capitalize;">' + col[i].replace("USD_M", "<br>USD (M) ").replace(/_/g, ' ') + '</div></div></th>');
						}

					}
					$.each(dat, function (key, value) {
						var i = 0;
						var tkrhtml = '<td><div class="left">' + value.value_date + '</div></td>'

						for (i = 0; i < col.length ; i++) {
							if (col[i].indexOf("_value") == -1) {
								if (col[i].indexOf("_mean") >=0) {
									var col_name = (col[i].split('_mean')[0]).split('analyst_estimate_')[1]
									var data = value[col_name + "_value"]
									var data2 = dat[((key>0)?(key - 1):0)][col_name + "_value"]
									if ((value.value_date == 'Acc/Dcc' && data2 != undefined) || value.value_date != 'Acc/Dcc')
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
									else {
										tkrhtml += '<td style="padding: .5rem;font-size: 14px;" data-start="" data-end="">' + ((value[col[i]] != null) ? ((value.value_date == 'Acc/Dcc') ? ((parseFloat(value[col[i]])).toFixed(2) + '%') : (parseFloat(value[col[i]])).toFixed(4)) : '-') + '</td>'
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
