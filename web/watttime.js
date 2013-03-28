// Copyright 2013 Google Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
// limitations under the License.
//
// Author: Eric Nguyen (ericnguyen@google.com)


// Globals. Don't judge.
var forecast;

// Utility function.
function makeParams(paramsObj) {
	var paramsArray = [];
	$.each(paramsObj, function(key, value) {
			paramsArray.push(key + '=' + value);
	});
  return paramsArray.join('&');
};

$(document).ready(function() {
    // Get current mix info.
		var url = 'http://108.59.82.94/api/';
		var mixParams = {
			'callback': '?',
			'ba': 'BPA'
    };
		$.getJSON(url + 'status?' + makeParams(mixParams), drawMix);
		var forecastParams = {
			'callback': '?',
			'ba': 'BPA'
    };
		$.getJSON(url + 'forecast?' + makeParams(forecastParams), drawNextbest);
		init();
});

function init() {
  $('#waitbtn').click(function() {
    $('#action').addClass('expandedpane');
  });
  $('#action input').click(function() {
    $(this)[0].checked = false;
    $('#action').removeClass('expandedpane');
    $('#thanks').show().addClass('expandedpane');
  });
  $('#donebtn').click(function() {
    $('#thanks').removeClass('expandedpane');
    $('#thanks').delay(250).hide(1);
  });
  $('#getforecastbtn').click(function() {
    var forecastEl = $('#forecast');
    if (forecastEl.is(':visible')) {
      $('#forecast').fadeOut(300);
    } else {
      $('#forecast').fadeIn(300);
      drawChart();
    }
  });
}

function drawMix(data) {
  var rainbow = new Rainbow(); 
  rainbow.setNumberRange(0, 100);
  rainbow.setSpectrum('000000', '99ff99');
  var percentGreen = Math.round(data.percent_green);
  var color = rainbow.colourAt(percentGreen);
  mixnumber = $('#mixnumber');
  mixnumber.text(percentGreen + '%').css({ 'color': color });
}

function drawNextbest(data) {
  forecast = data.forecast;
  var greenestHour = data.forecast[0];
  $.each(data.forecast, function(index, hourForecast) {
    if (hourForecast.percent_green > greenestHour.percent_green) {
      greenestHour = hourForecast;
    }
  });
  $('#getforecastbtn').text(greenestHour.hour + ' hours');
}

function drawChart() {
  if (!forecast) return;

  var forecastData = [['Hours from now', 'Percent Clean']];
  $(forecast).each(function(index, forecastObj) {
    forecastData.push([
      forecastObj.hour + 'hrs',
      forecastObj.percent_green
    ]);
  });
  var data = google.visualization.arrayToDataTable(forecastData);

  var options = {
    title: '24-hour Power Mix Forecast',
    backgroundColor: '#efe',
    fontName: 'Quicksand',
    titleTextStyle: {fontSize: 18, color: '#090'},
    lineWidth: 4,
    colors: ['#090'],
    legend: {position: 'none'}
  };

  var chart = new google.visualization.LineChart(document.getElementById('forecast'));
  chart.draw(data, options);
}
