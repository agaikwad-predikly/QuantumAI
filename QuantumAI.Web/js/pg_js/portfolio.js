$(document).ready(function ($) {

    "use strict";
    if (localStorage.getItem("is_login") != 1) {
        window.location.href = "/login.html"
    }
    else {
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
    		BindMonthlyData(portoflio_dt_full, indicator_type, target_type, strength, limit);
    		var i = 0;
    		for (i = 1; i < parseInt($("#ddl_no_of_month").val()) ; i++) {
    			var dt = moment(portoflio_dt_full).add(i, 'M').toDate();
    			BindMonthlyData(dt, indicator_type, target_type, strength, limit);
    		}
    	});

    	function ResetBuySellTBL(){
    		$('.buy_sell_tbl').empty();
    		$('.top_buysell-dtl .progress-info').empty();
    		$('.bottom_buysell-dtl .progress-info').empty();

    		$('.buy_sell_tbl').html('<thead><tr><th style="background-color: #e0dfdf;">Acc/Dec</th></tr></thead><tbody>');
    	}

    	function BindMonthlyData(portoflio_dt_full, indicator_type, target_type, strength, limit) {
    		if($('.buy_sell_tbl thead').find('th.head_mon_'+portoflio_dt_full.getMonth())==undefined || $('.buy_sell_tbl thead').find('th.head_mon_'+portoflio_dt_full.getMonth()).length == 0){
    			$('.buy_sell_tbl thead tr').append('<th class="head_mon_' + portoflio_dt_full.getMonth() + '"><div class="status font-14">	<div class="status-title">' + moment(portoflio_dt_full).format("MMM") + ' ' + portoflio_dt_full.getFullYear() + '</div><div class="status-number"></div></div></th>')
    		}
    		 
    	
    		var portoflio_dt = moment(portoflio_dt_full).format("YYYY-MM-DD HH:mm:ss");
    		var form = new FormData();
    		var settings = {
    			"async": true,
    			"crossDomain": true,
    			"url": "http://localhost:50515/portfolio_predict_month?date=" + portoflio_dt + "&indicator_type=" + indicator_type + "&target_type=" + target_type + "&adv_weight=" + strength + "&limit=" + limit,
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
    					var columnIndex = $('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth()).index();
    					if (columnIndex == 1) {
    						$.each(data.slice(0, 3), function (key, value) {
    							$('.top_buysell-dtl .progress-info').append('<div class="status font-14">	<div class="status-title">' + value.ticker_symbol + '</div><div class="status-number"> ' + (value.percent_gain).toFixed(2) + '% </div><div class="status-number">' + (value.price_gain).toFixed(2) + '</div></div>');
    						});

    						$.each(data.slice(-3).reverse(), function (key, value) {
    							$('.bottom_buysell-dtl .progress-info').append('<div class="status font-14">	<div class="status-title">' + value.ticker_symbol + '</div><div class="status-number"> ' + (value.percent_gain).toFixed(2) + '% </div><div class="status-number">' + (value.price_gain).toFixed(2) + '</div></div>');
    						});
    					}

						var colcnt = 0
    					var total_gain = 0;
    					$.each(data, function (key, value) {
    						total_gain = total_gain + ((value.percent_gain != null && value.percent_gain != '') ? value.percent_gain : 0);
    						colcnt = colcnt + 1;
    						if ($('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id) == undefined || $('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).length == 0) {

    							var tkrhtml = '<td class="tkr_' + value.ticker_id + '"><div class="left">' + value.ticker_symbol
											+ '<span class="tkr-fullname">' + ((value.is_newly_added == 1 && columnIndex==1) ? '<i class="fa fa-star"></i>' : '') + value.ticker_name + '</span>'
											+ '</div><a class="right" data-toggle="modal" data-target="#modal_graph"><i class=" fa fa-line-chart" style="color: #0ba1c7;"></i></a></td>'

    							var i = 0;
    							for (i = 0; i < ($(".buy_sell_tbl thead").find('tr')[0].cells.length - 1) ; i++) {
    								tkrhtml += '<td></td>'
    							}
    							$('.buy_sell_tbl tbody').append('<tr>' + tkrhtml + '</tr>')
    						}
    							$('.buy_sell_tbl tbody').find('td.tkr_' + value.ticker_id).closest('tr').find('td').eq(columnIndex).html('<div class="clearfix"><div class="left">' + (value.percent_gain).toFixed(2) + '%</div></div>' + ((target_type == 1) ? '<div class="text_buy_sell_status buy">B</div>' : '<div class="text_buy_sell_status sell">S</div>'))
    						
    					});

    					if (total_gain !=0) {
    						total_gain = total_gain / colcnt;
    						$('.buy_sell_tbl thead').find('th.head_mon_' + portoflio_dt_full.getMonth()).find('.status-number').html(total_gain.toFixed(2) + '%')
    					}
    				}
    			}
    		});
    	}
    }
});