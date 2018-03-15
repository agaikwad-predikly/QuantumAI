var is_request_complete = 0;
$(document).ready(function ($) {
    "use strict";
    if (localStorage.getItem("is_login") != 1) {
        window.location.href = "/login.html"
    }
    else {
    	$('#init_msg_div').show();
    	$('#init_msg').show();
    	$('.portfolio-tkr-items').hide();
    	$('.page').show();
    	ChangeStrength();
    	$('.dt_picker').datepicker({
    		format: "M-yyyy",
    		viewMode: "months", 
    		minViewMode: "months",
    		autoclose: 'true'
    	}).datepicker("setDate", new Date());

    	$('#ddl_indicator').change(function (e) {
    		ChangeStrength();
    	});

    	$('#ddl_target').change(function (e) {
    		ChangeStrength();
    	});
    	$("#btnExcelExport").click(function () {
    		if (is_request_complete == 1) {
    			if ($.ajaxQ.get_remaining_cnt() == 0) {
    				var portoflio_dt_full = new Date("01-" + $('#portfolio_date').val());
    				var limit = $('#ddl_limit').val();
    				var indicator_type = $('#ddl_indicator').val();
    				var target_type = $('#ddl_target').val();
    				var strength = $('#txtstrength').val();
    				var filename = "Top_" + limit + "_" + (($('#ddl_target').val() == "1") ? "BUY" : "SHORT/SELL") + "_portfolios_by_" + (($('#ddl_indicator').val() == 'XF') ? 'fundamental' : ($('#ddl_indicator').val() == 'XT') ? "technical" : 'fundamental_and_technical') + ".xls";
    				var worksheetname = "Top_" + limit + "_" + (($('#ddl_target').val() == "1") ? "BUY" : "SHORT/SELL") + "_portfolios_by_" + $('#ddl_indicator').val();
    				var html = $('.buy_sell_tbl').html()
    				$('.buy_sell_tbl').find('.text_buy_sell_status').remove();
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
    			if ($('#ddl_target').val() == "1") {
    				$('#txtstrength').val("20");
    				$('#spn_angle_sign').find('i').removeClass('fa-angle-left').addClass('fa-angle-right');
    			} else {
    				$('#txtstrength').val("0");
    				$('#spn_angle_sign').find('i').removeClass('fa-angle-right').addClass('fa-angle-left');
    			}
    		}
    		else {
    			$('#txtstrength').val("0");
    			$('#txtstrength').attr("disabled", "disabled");
    		}
    	}

    	$('#btnRecommend').click(function (e) {
    		e.preventDefault();
    		var portoflio_dt_full = new Date("01-" + $('#portfolio_date').val());
			var limit = $('#ddl_limit').val();
    		var indicator_type = $('#ddl_indicator').val();
    		var target_type = $('#ddl_target').val();
    		var strength = $('#txtstrength').val();
    		ResetBuySellTBL();
    		$.blockUI();
    		var text = ["Request accepted by server", "Data validated","Gathering Data", "Processing Request", "Calculating the Gains", "Creating Portfolio", "Your Portfolio is ready."];
    		var counter = 0;
    		var elem = document.getElementById("loader_msg");
    		var imgelem = document.getElementById("_loading_img");
    		var inst = setInterval(change, 3000);

    		function change() {
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

    		var i = 0;
    		for (i = 0; i < parseInt($("#ddl_no_of_month").val()) ; i++) {
    			var dt = moment(portoflio_dt_full).add(i, 'M').toDate();
    			if ($('.buy_sell_tbl thead').find('th.head_mon_' + dt.getMonth() + "_" + dt.getFullYear()) == undefined || $('.buy_sell_tbl thead').find('th.head_mon_' + dt.getMonth() + "_" + dt.getFullYear()).length == 0) {
    				$('.buy_sell_tbl thead tr').append('<th class="head_mon_' + dt.getMonth() + "_" + dt.getFullYear() + '"><div class="status font-14">	<div class="status-title text-center">' + moment(dt).format("MMM") + ' ' + dt.getFullYear() + '</div><div class="status-number"><div class="left _tkr_month_count"></div><div class="right _tkr_month_percent_gain"></div></div></div></th>')
					
    			}
    		}

    		BindMonthlyData(portoflio_dt_full, indicator_type, target_type, strength, limit);
    		var inst2 = setInterval(executefor_othermnth.bind(null, portoflio_dt_full, indicator_type, target_type, strength, limit), 3000);
    		function executefor_othermnth(portoflio_dt_full, indicator_type, target_type, strength, limit) {
    			if (is_request_complete == 1) {
    				var i = 0;
    				for (i = 1; i < parseInt($("#ddl_no_of_month").val()) ; i++) {
    					var dt = moment(portoflio_dt_full).add(i, 'M').toDate();
    					BindMonthlyData(dt, indicator_type, target_type, strength, limit);
    				}
    				clearInterval(inst2);

    			}
    		}

    		var inst3 = setInterval(CalculateTickerYrReturn.bind(null, target_type), 3000);

    		function CalculateTickerYrReturn(target_type) {
    			if ($.ajaxQ.get_remaining_cnt() == 0) {

    				$('.buy_sell_tbl tbody tr').each(function () {
    					var yr_return = 0; var start_close_price = null; var end_close_price = null; var i = 0;
    					var tdlength = $(this).find('td').not(':first').length;
    					var ticker_id = $(this).find('td:first').attr('data-ticker');
    					$(this).find('td').not(':first').each(function (index, ele) {
    						i++;
    						var tr_start_close_price = parseFloat($(this).attr('data-start'));
    						if (tr_start_close_price == null || tr_start_close_price == undefined || tr_start_close_price == '' || isNaN(tr_start_close_price)) {
    							tr_start_close_price = null;
    						}

    						var tr_end_close_price = parseFloat($(this).attr('data-end'));
    						if (tr_end_close_price == null || tr_end_close_price == undefined || tr_end_close_price == '' || isNaN(tr_end_close_price)) {
    							tr_end_close_price = null;
    							i = i - 1;
    						}

    						if (tr_start_close_price != null && start_close_price == null) {
    							start_close_price = tr_start_close_price;
    						}
							
    						if ((tr_end_close_price == null || index == (tdlength - 1)) && start_close_price != null && end_close_price != null) {
    							if (tr_end_close_price != null || index == (tdlength - 1)) {
    								end_close_price = tr_end_close_price;
    							}
    							if (target_type == 1) {
    								yr_return = yr_return + (((end_close_price - start_close_price) / start_close_price) * 100)
    							}
    							else {
    								yr_return = yr_return + (((start_close_price - end_close_price) / start_close_price) * 100)
    							}
    							start_close_price = null;
    							end_close_price = null;
    						}
    						else if (tr_end_close_price != null && start_close_price != null) {
    							end_close_price = tr_end_close_price;
    						}
    					});

    					if (isFinite(yr_return)) {
    						$(this).find('td:first-child').find('._tkr_yr_rtn').removeClass('negative').addClass((yr_return < 0) ? 'negative' : '').html(((yr_return < 0) ? ("(" + yr_return.toFixed(2) + ")") : yr_return.toFixed(2)) + "%/" + i);
    						if ($('.top_buysell-dtl .progress-info').find('.tkr_tb_' + ticker_id) != undefined && $('.top_buysell-dtl .progress-info').find('.tkr_tb_' + ticker_id).length > 0) {
    							$('.top_buysell-dtl .progress-info').find('.tkr_tb_' + ticker_id).find('.tkr_total_gain').html(yr_return.toFixed(2));
    						}
    						if ($('.bottom_buysell-dtl .progress-info').find('.tkr_tb_' + ticker_id) != undefined && $('.bottom_buysell-dtl .progress-info').find('.tkr_tb_' + ticker_id).length > 0) {
    							$('.bottom_buysell-dtl .progress-info').find('.tkr_tb_' + ticker_id).find('.tkr_total_gain').html(yr_return.toFixed(2));
    						}
    					}
    				});

    				clearInterval(inst3);

    			}
    		}


    	});

    	function CalculateYearlyReturns(totalreturn) {
    		var current_total = parseFloat($('#total_yrl_rtn').html());
    		if (current_total == null || current_total == undefined || current_total == '' || isNaN(current_total)) {
    			current_total = 0;
    		}

    		var totalyrreturn =(current_total + totalreturn);
    		if (isFinite(totalyrreturn)) {
    			$('#total_yrl_rtn').removeClass('negative').addClass((totalyrreturn < 0) ? 'negative' : '').html(totalyrreturn.toFixed(2));
    		}
    	}

    	function ResetBuySellTBL() {
    		$.ajaxQ.abortAll();
    		$('.portfolio-tkr-items').hide();
    		$('#init_msg_div').show();
    		is_request_complete = 0;
    		$('#init_msg').hide();
    		$('.buy_sell_tbl').empty();
    		$('.top_buysell-dtl .progress-info').empty();
    		$('.bottom_buysell-dtl .progress-info').empty();
    		if ($('#ddl_target').val() == "1") {
    			$('.top_buysell-dtl').find('.top_tkr_header').html('Top 5 BUY\'s');
    			$('.bottom_buysell-dtl').find('.bottom_tkr_header').html('Bottom 5 BUY\'s');
    		}
    		else {
    			$('.top_buysell-dtl').find('.top_tkr_header').html('Top 5 SELL\'s');
    			$('.bottom_buysell-dtl').find('.bottom_tkr_header').html('Bottom 5 SELL\'s');
    		}
    		$('.buy_sell_tbl').html('<thead><tr><th style="background-color: #e0dfdf;"><div class="status font-bold" style="margin-bottom: 28px;"><div class="status-title left" style="margin-top: 6px;">' + $("#ddl_no_of_month").val() + 'M % Returns</div><div class="status-number right"  style="font-size: 24px;"><span id="total_yrl_rtn"></span>%</div></div></th></tr></thead><tbody>');
    	}

    	function BindMonthlyData(portoflio_dt_full, indicator_type, target_type, strength, limit) {
    		
    		var portoflio_dt = moment(portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
    		var form = new FormData();
    		var settings = {
    			"async": true,
    			"crossDomain": true,
    			"url": $.api_base_url + "/portfolio_predict_month?date=" + portoflio_dt + "&indicator_type=" + indicator_type + "&target_type=" + target_type + "&adv_weight=" + strength + "&limit=" + limit,
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
    					if (columnIndex == 1) {
    						$.each(data.slice(0, 5), function (key, value) {
    							$('.top_buysell-dtl .progress-info').append('<div class="status font-14 tkr_tb_' + value.ticker_id + '">	<div class="status-title left">' + value.ticker_symbol + '</div><div class="status-number right tkr_total_gain"> ' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) + "%") : '') + ' </div></div>');
    						});

    						$.each(data.slice(-5).reverse(), function (key, value) {
    							$('.bottom_buysell-dtl .progress-info').append('<div class="status font-14 tkr_tb_' + value.ticker_id + '">	<div class="status-title left">' + value.ticker_symbol + '</div><div class="status-number right tkr_total_gain"> ' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) + "%") : '') + ' </div></div>');
    						});
    					}

						var colcnt = 0
    					var total_gain = 0;
    					$.each(data, function (key, value) {
    						total_gain = total_gain + ((value.percent_gain != null && value.percent_gain != '') ? value.percent_gain : 0);
    						colcnt = colcnt + 1;
    						if ($('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id) == undefined || $('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).length == 0) {

    							var tkrhtml = '<td class="tkr_' + value.ticker_id + '" data-ticker="'+ value.ticker_id +'"><div class="left"><a  data-toggle="modal" data-target="#modal_graph">' + value.ticker_symbol + '</a>'
											+ '<span class="tkr-fullname">' + ((value.is_newly_added == 1 && columnIndex==1) ? '<i class="fa fa-star"></i>' : '') + value.ticker_name + '</span>'
											+ '</div><div class="right"><div class="right _tkr_yr_rtn"></div></td>'

    							var i = 0;
    							for (i = 0; i < ($(".buy_sell_tbl thead").find('tr')[0].cells.length - 1) ; i++) {
    								tkrhtml += '<td data-start="" data-end=""></td>'
    							}
    							$('.buy_sell_tbl tbody').append('<tr>' + tkrhtml + '</tr>')
    						}
    						$('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).closest('tr').find('td').eq(columnIndex).attr('data-start', ((value.f_close_price != null) ? value.f_close_price : "")).attr('data-end', ((value.l_close_price != null) ? value.l_close_price : "")).addClass((value.percent_gain > 0) ? 'buy' : ((value.percent_gain < 0) ? 'sell' : '')).html('<div class="clearfix"><div class="left">' + ((value.percent_gain != null) ? ((value.percent_gain).toFixed(2) + "%") : '-') + '</div></div>' + ((target_type == 1) ? '<div class="text_buy_sell_status buy">B</div>' : '<div class="text_buy_sell_status sell">S</div>'));
    					});

    					if (total_gain !=0) {
    						total_gain = total_gain / colcnt;
    						$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_percent_gain').addClass((total_gain < 0) ? 'negative' : '').html(total_gain.toFixed(2) + '%')
    						$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_count').html('#' + colcnt);
    					} else {
    						$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_percent_gain').html('-')
    						$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth() + '_' + portoflio_dt_full.getFullYear()).find('._tkr_month_count').html('#' + colcnt);

    					}

    					is_request_complete = 1;
    					CalculateYearlyReturns(total_gain);
    					//CalculateTickerYrReturn(target_type);
    				}
    			}
    		});
    	}
    }
});