$(document).ready(function() {
	Highcharts.setOptions({
		lang: {
			numericSymbols: null
		}
	});
	var loadCharts= function (duration){
		url = '/admin/chart_data/'+ duration
		console.log(url)
		request = $.getJSON(url);
	request.done(function (data) {  // success callback
		apiData = data[0];

		highChartInfo = {
				chart : {renderTo: "#" + apiData.chart.renderTo, type: apiData.chart.type, height: 500},
				plotOptions:{line: {dataLabels: {enabled: apiData.plotOptions.line.dataLabels.enabled}, enableMouseTracking: apiData.plotOptions.line.enableMouseTracking}},
				title:{text: apiData.title.text},
				xAxis: {categories: apiData.xAxis.categories},
				yAxis: {title: {text: apiData.yAxis.title.text}, max: apiData.yAxis.max},
				series: [{name: apiData.series[0].name,data: apiData.series[0].data}, 
				{name: apiData.series[1].name,data: apiData.series[1].data}],
			}
		// console.log(highChartInfo);
		  $( "#" + apiData.chart.renderTo).highcharts(highChartInfo);
    });
	
	}
	loadCharts("30")
	

	$(".timeframe").change(function(){
		var $option = $(this).find('option:selected');
		loadCharts($option.val())
	  });
});