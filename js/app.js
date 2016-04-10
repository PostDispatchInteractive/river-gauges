// using a closure to protect global variables
(function () {

	// global variables for leaflet maps
	var gaugeMap = false;
	var gaugeMarkerLayer = L.featureGroup();

	//
	// To Title Case 2.1 – http://individed.com/code/to-title-case/
	// Copyright © 2008–2013 David Gouch. Licensed under the MIT License.
	//

	String.prototype.toTitleCase = function(){
		var smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|nor|of|on|or|per|the|to|vs?\.?|via)$/i;
		that = this.toLowerCase();

		return that.replace(/[A-Za-z0-9\u00C0-\u00FF]+[^\s-\/]*/g, function(match, index, title){
			if (index > 0 && index + match.length !== title.length &&
				match.search(smallWords) > -1 && title.charAt(index - 2) !== ":" &&
				(title.charAt(index + match.length) !== '-' || title.charAt(index - 1) === '-') &&
				title.charAt(index - 1).search(/[^\s-]/) < 0) {
				return match.toLowerCase();
			}

			if (match.substr(1).search(/[A-Z]|\../) > -1) {
				return match;
			}

			return match.charAt(0).toUpperCase() + match.substr(1);
		});
	};


	/**
	* js-date-format (js-date-format.js)
	* v1.0
	* (c) Tony Brix (tonybrix.info) - 2014.
	* https://github.com/UziTech/js-date-format
	*
	* MIT License
	*
	* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
	* associated documentation files (the "Software"), to deal in the Software without restriction,
	* including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
	* and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
	* subject to the following conditions:
	*
	* The above copyright notice and this permission notice shall be included in all copies or substantial
	* portions of the Software.
	*
	* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
	* NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
	* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
	* WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
	* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
	*/
	Date.prototype.setLocale = function (lang) {
		if (lang && lang in Date.locales) {
			this.locale = lang;
		}
	};

	Date.prototype.getLocale = function () {
		return this.locale || "en";
	};

	Date.prototype.getMonthName = function (lang) {
		var locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].month_names[this.getMonth()];
	};

	Date.prototype.getMonthNameShort = function (lang) {
		var locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].month_names_short[this.getMonth()];
	};

	Date.prototype.getDayName = function (lang) {
		var locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].day_names[this.getDay()];
	};

	Date.prototype.getDayNameShort = function (lang) {
		var locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].day_names_short[this.getDay()];
	};

	Date.prototype.getDateSuffix = function (lang) {
		var locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].date_suffix(this.getDate());
	};

	Date.prototype.getMeridiem = function (isLower, lang) {
		var locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].meridiem(this.getHours(), this.getMinutes(), isLower);
	};

	Date.prototype.getLastDate = function () {
		return (new Date(this.getFullYear(), this.getMonth() + 1, 0)).getDate();
	};

	/* languages from http://momentjs.com */
	Date.locales = {
		"en": {
			month_names: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
			month_names_short: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
			day_names: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
			day_names_short: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
			date_suffix: function (date) {
				var day10 = ~~ (date % 100 / 10);
				var day1 = date % 10;
				if (day10 === 1) {
					return "th";
				} else if (day1 === 1) {
					return "st";
				} else if (day1 === 2) {
					return "nd";
				} else if (day1 === 3) {
					return "rd";
				} else {
					return "th";
				}
			},
			meridiem : function (hour, minute, isLower) {
				if (hour < 12) {
					return isLower ? "am" : "AM";
				} else {
					return isLower ? "pm" : "PM";
				}
			}
		}
	};

	Date.prototype.format = function (formatString) {

		var addPadding = function (value, length) {
			var negative = ((value < 0) ? "-" : "");
			var zeros = "0";
			for (var i = 2; i < length; i++) {
				zeros += "0";
			}
			return negative + (zeros + Math.abs(value).toString()).slice(-length);
		};

		var replacements = {
			date: this,
			YYYY: function () {
				return this.date.getFullYear();
			},
			YY: function () {
				return this.date.getFullYear() % 100;
			},
			MMMM: function () {
				return this.date.getMonthName();
			},
			MMM: function () {
				return this.date.getMonthNameShort();
			},
			MM: function () {
				return addPadding((this.date.getMonth() + 1), 2);
			},
			M: function () {
				return this.date.getMonth() + 1;
			},
			DDDD: function () {
				return this.date.getDayName();
			},
			DDD: function () {
				return this.date.getDayNameShort();
			},
			DD: function () {
				return addPadding(this.date.getDate(), 2);
			},
			D: function () {
				return this.date.getDate();
			},
			S: function () {
				return this.date.getDateSuffix();
			},
			HH: function () {
				return addPadding(this.date.getHours(), 2);
			},
			H: function () {
				return this.date.getHours();
			},
			hh: function () {
				var hour = this.date.getHours();
				if (hour > 12) {
					hour -= 12;
				} else if (hour < 1) {
					hour = 12;
				}
				return addPadding(hour, 2);
			},
			h: function () {
				var hour = this.date.getHours();
				if (hour > 12) {
					hour -= 12;
				} else if (hour < 1) {
					hour = 12;
				}
				return hour;
			},
			mm: function () {
				return addPadding(this.date.getMinutes(), 2);
			},
			m: function () {
				return this.date.getMinutes();
			},
			ss: function () {
				return addPadding(this.date.getSeconds(), 2);
			},
			s: function () {
				return this.date.getSeconds();
			},
			fff: function () {
				return addPadding(this.date.getMilliseconds(), 3);
			},
			ff: function () {
				return addPadding(Math.floor(this.date.getMilliseconds() / 10), 2);
			},
			f: function () {
				return Math.floor(this.date.getMilliseconds() / 100);
			},
			zzzz: function () {
				return addPadding(Math.floor(-this.date.getTimezoneOffset() / 60), 2) + ":" + addPadding(-this.date.getTimezoneOffset() % 60, 2);
			},
			zzz: function () {
				return Math.floor(-this.date.getTimezoneOffset() / 60) + ":" + addPadding(-this.date.getTimezoneOffset() % 60, 2);
			},
			zz: function () {
				return addPadding(Math.floor(-this.date.getTimezoneOffset() / 60), 2);
			},
			z: function () {
				return Math.floor(-this.date.getTimezoneOffset() / 60);
			},
			tt: function () {
				return this.date.getMeridiem(true);
			},
			TT: function () {
				return this.date.getMeridiem(false);
			}
		};


		var formats = new Array();
		while (formatString.length > 0) {
			if (formatString[0] === "\"") {
				var temp = /"[^"]*"/m.exec(formatString);
				if (temp === null) {
					formats.push(formatString.substring(1));
					formatString = "";
				} else {
					temp = temp[0].substring(1, temp[0].length - 1);
					formats.push(temp);
					formatString = formatString.substring(temp.length + 2);
				}
			} else if (formatString[0] === "'") {
				var temp = /'[^']*'/m.exec(formatString);
				if (temp === null) {
					formats.push(formatString.substring(1));
					formatString = "";
				} else {
					temp = temp[0].substring(1, temp[0].length - 1);
					formats.push(temp);
					formatString = formatString.substring(temp.length + 2);
				}
			} else if (formatString[0] === "\\") {
				if (formatString.length > 1) {
					formats.push(formatString.substring(1, 2));
					formatString = formatString.substring(2);
				} else {
					formats.push("\\");
					formatString = "";
				}
			} else {
				var foundMatch = false;
				for (var i = formatString.length; i > 0; i--) {
					if (formatString.substring(0, i) in replacements) {
						formats.push(replacements[formatString.substring(0, i)]());
						formatString = formatString.substring(i);
						foundMatch = true;
						break;
					}
				}
				if (!foundMatch) {
					formats.push(formatString[0]);
					formatString = formatString.substring(1);
				}
			}
		}

		return formats.join("");
	};





	// -----------------
	// APP FUNCTIONS
	// -----------------

	urlParam = function(name) {
		var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
		if (results==null){
			return null;
		}
		else {
			return results[1] || 0;
		}
	}


	function getJsonData(url) {
		return $.ajax({
			url: url,
			type: "GET",
			dataType: "json"
		});
	}

	function dynamicSort(property) {
		var sortOrder = 1;
		if(property[0] === "-") {
			sortOrder = -1;
			property = property.substr(1);
		}
		return function (a,b) {
			var result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
			return result * sortOrder;
		}
	}


	// -----------------
	// INITIALIZER
	// -----------------

	function initialize(a) {
		var pymChild = new pym.Child();

		var gaugeData = a;
		// console.log(gaugeData);

		// - - - - - - - - -
		// gauge MAP  (with markers)
		// - - - - - - - - -

		if (!gaugeMap) {
			gaugeMap = new L.map('gauge-map', { 
				zoomControl: true,
				scrollWheelZoom: false
			});
			gaugeMap.setView(new L.LatLng(38.65, -90.2426),11);
		}

		gaugeMarkerLayer.clearLayers();

		L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
			attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
			maxZoom: 18,
//			id: 'jeremykohler.jh121oin',
			id: 'jeremykohler.k1gj1ge9',
			accessToken: 'pk.eyJ1IjoiamVyZW15a29obGVyIiwiYSI6IkNfbVM2WFEifQ.PaWz-wfdL9ACYU0uTY89qg'
		}).addTo(gaugeMap);

		// The '-' tells dynamicSort to sort in reverse
		gaugeData.sort( dynamicSort('Location') );


		for (var i=0; i<gaugeData.length; i++) {
			var gauge = gaugeData[i];
			if (gauge['Latitude'] && gauge['Longitude']) {

				var status = gauge['Status'];
				var location = gauge['Location'].toString();
				var river = gauge['Waterbody'].toString().replace(' River','');
				// Only generate data if there is actually a forceast
				if (status) {
					var fd = gauge['FcstTime'].split(/[^0-9]/);
					var forecast_date = new Date( fd[0], fd[1]-1, fd[2]  ).getDayName();
					var fi = gauge['FcstIssunc'].split(/[^0-9]/);
					var forecast_issue_date = new Date( fi[0], fi[1]-1, fi[2] ).toDateString();
					var forecast = gauge['Forecast'];
					var units = gauge['Units'];
				}
				else {
					var forecast_date = 'N/A'
					var forecast_issue_date = null;
					var forecast = 'N/A';
					var units = '';
				}
				var level_action = gauge['Action'];
				var level_flood = gauge['Flood'];
				var level_moderate = gauge['Moderate'];
				var level_major = gauge['Major'];
				var url = gauge['URL'];
				var record = gauge['record-level'];
				var rd = gauge['record-date'].split(/[^0-9]/);
				var record_date = new Date( rd[0], rd[1]-1, rd[2] ).format('MMM D, YYYY');

				var iconColor = '';
				switch (status){
					case 1:
						iconColor = "#0c0";
						break;
					case 2:
						iconColor = "#ff0";
						break;
					case 3:
						iconColor = "#f90";
						break;
					case 4:
						iconColor = "#c00";
						break;
					case 5:
						iconColor = "#60c";
						break;
				}
				if ( status < 1 || status > 5 )
					var icon = L.MakiMarkers.icon({icon: null, color: '#000', size: "m"});

				else
					var icon = L.MakiMarkers.icon({icon: null, color: iconColor, size: "m"});

				var marker = L.marker([ gauge['Latitude'], gauge['Longitude'] ], {icon: icon} );

				marker.bindPopup(
					'<h3>' + location + '</h3>' +
					'<p><strong>River</strong>: ' + river + '</p>' +
					'<p><strong>Forecast </strong>: ' + forecast + ' ' + units + ' on ' + forecast_date +'</p>' +
					// '<p><strong>Forecast issued </strong>: ' + forecast_issue_date + '</p>' +
					'<p><strong>Action</strong>: ' + level_action + ' ' + units + '</p>' +
					'<p><strong>Flood</strong>: ' + level_flood + ' ' + units + '</p>' +
					'<p><strong>Moderate</strong>: ' + level_moderate + ' ' + units + '</p>' +
					'<p><strong>Major</strong>: ' + level_major + ' ' + units + '</p>'
				)
				gaugeMarkerLayer.addLayer(marker);

				var tableRow =
					'<tr>' +
	                    '<td><span class="color' + status + '"></span></td>' +
	                    '<td>' + location + '</td>' +
	                    '<td>' + river + '</td>' +
	                    '<td>' + forecast + ' ' + units + '</td>' +
	                    '<td>' + forecast_date + '</td>' +
	                    // Records are always in feet.
	                    '<td>' + record + ' ' + 'ft' + '</td>' +
	                    '<td>' + record_date + '</td>' +
	                    '<td>' + level_action + ' ' + units + '</td>' +
	                    '<td>' + level_flood + ' ' + units + '</td>' +
	                    '<td>' + level_moderate + ' ' + units + '</td>' +
	                    '<td>' + level_major + ' ' + units + '</td>' +
					'</tr>';
				// console.log(tableRow);
				$('#gauge-table table tbody').append(tableRow);

			}

		}


		gaugeMap.addLayer( gaugeMarkerLayer );
		// zoom and re-center gauge map to fit the selected neighborhood
		gaugeMap.fitBounds( gaugeMarkerLayer.getBounds() );

		pymChild.sendHeight();


	} // initialize()







	// ready handler
	jQuery(document).ready(function($) {

		var gaugesUrl = 'http://graphics.stltoday.com/data/weather/river-gauges/local_river_gauges.json';

		// Grab the crime and map data files. Once BOTH are loaded, initialize the app.
		$.when(
			getJsonData(gaugesUrl)
		)
		.done(
			function(a) {
				// call the initializer
				initialize(a);
			}
		);

	}); // jQuery ready()


})(); //app closure










