// using a closure to protect global variables
(function () {

	// global variables for leaflet maps
	let map = false;
	let marker_layers = {
		'current': L.featureGroup(),
		'forecast': L.featureGroup()
	};
	const pymChild = new pym.Child();

	//
	// To Title Case 2.1 – http://individed.com/code/to-title-case/
	// Copyright © 2008–2013 David Gouch. Licensed under the MIT License.
	//

	String.prototype.toTitleCase = function(){
		let smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|nor|of|on|or|per|the|to|vs?\.?|via)$/i;
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
		let locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].month_names[this.getMonth()];
	};

	Date.prototype.getMonthNameShort = function (lang) {
		let locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].month_names_short[this.getMonth()];
	};

	Date.prototype.getDayName = function (lang) {
		let locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].day_names[this.getDay()];
	};

	Date.prototype.getDayNameShort = function (lang) {
		let locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].day_names_short[this.getDay()];
	};

	Date.prototype.getDateSuffix = function (lang) {
		let locale = "en";
		if (lang && lang in Date.locales) {
			locale = lang;
		} else if (this.locale && this.locale in Date.locales) {
			locale = this.locale;
		}
		return Date.locales[locale].date_suffix(this.getDate());
	};

	Date.prototype.getMeridiem = function (isLower, lang) {
		let locale = "en";
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
				let day10 = ~~ (date % 100 / 10);
				let day1 = date % 10;
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

		let addPadding = function (value, length) {
			let negative = ((value < 0) ? "-" : "");
			let zeros = "0";
			for (let i = 2; i < length; i++) {
				zeros += "0";
			}
			return negative + (zeros + Math.abs(value).toString()).slice(-length);
		};

		let replacements = {
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
				let hour = this.date.getHours();
				if (hour > 12) {
					hour -= 12;
				} else if (hour < 1) {
					hour = 12;
				}
				return addPadding(hour, 2);
			},
			h: function () {
				let hour = this.date.getHours();
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


		let formats = new Array();
		while (formatString.length > 0) {
			if (formatString[0] === "\"") {
				let temp = /"[^"]*"/m.exec(formatString);
				if (temp === null) {
					formats.push(formatString.substring(1));
					formatString = "";
				} else {
					temp = temp[0].substring(1, temp[0].length - 1);
					formats.push(temp);
					formatString = formatString.substring(temp.length + 2);
				}
			} else if (formatString[0] === "'") {
				let temp = /'[^']*'/m.exec(formatString);
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
				let foundMatch = false;
				for (let i = formatString.length; i > 0; i--) {
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
		const results = new RegExp('[\?&]${name}=([^&#]*)').exec(window.location.href);
		if (results==null){
			return null;
		}
		else {
			return results[1] || 0;
		}
	}


	function dynamicSort(property) {
		let sortOrder = 1;
		if(property[0] === "-") {
			sortOrder = -1;
			property = property.substr(1);
		}
		return function (a,b) {
			const result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
			return result * sortOrder;
		}
	}

	function catToInt(floodCategory) {
		if (['no_forecast','not_defined','obs_not_current','out_of_service','low_threshold'].includes(floodCategory)) {
			return null
		}
		if (floodCategory == 'no_flooding') {
			return 1;
		}
		if (floodCategory == 'action') {
			return 2;
		}
		if (floodCategory == 'minor') {
			return 3;
		}
		if (floodCategory == 'moderate') {
			return 4;
		}
		if (floodCategory == 'major') {
			return 5;
		}
		return null;
	}

	// -----------------
	// INITIALIZER
	// -----------------

	function initialize(responses) {

		data = responses[0];

		// - - - - - - - - -
		// gauge MAP  (with markers)
		// - - - - - - - - -

		if (!map) {
			map = new L.map('interactive-map', {
				zoomControl: true,
				scrollWheelZoom: false
			});
			map.setView(new L.LatLng(38.65, -90.2426),8);
		}

		for (l in marker_layers) {
			marker_layers[l].clearLayers();
		}

		// These are open street map tiles. Remember to include the attribution
		let tile_layer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}' + (L.Browser.retina ? '@2x.png' : '.png'), {
			attribution: 'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, Tiles &copy; <a href="https://carto.com/attributions">CARTO</a>',
			// minZoom: 8,
			// maxZoom: 16,
			subdomains: 'abcd',
			ext: 'png'
		}).addTo(map);


		// Pre-process the data to split the `name` field into `river` and `location`.
		// Doing this first makes it easier to sort the array by location.
		for (let i=0; i<data.length; i++) {
			let sep = ' at '
			if (!data[i]['name'].includes(sep)) { sep = ' near '}
			data[i]['river'] = data[i]['name'].split(sep)[0];
			data[i]['location'] = data[i]['name'].split(sep)[1];
		}

		// The '-' tells dynamicSort to sort in reverse
		data.sort( dynamicSort('location') );

		for (l of ['current', 'forecast']) {

			for (let i=0; i<data.length; i++) {
				const gauge = data[i];
				if (gauge['latitude'] && gauge['longitude']) {

					let river,
						location,
						forecast,
						forecast_date,
						level_action,
						level_minor,
						level_moderate,
						level_major,
						status,
						observed,
						observed_date,
						record,
						record_date;

					river = gauge['river'];
					location = gauge['location'];

					let today_obj = new Date();

					// Only generate observed data if there is actually an observed level
					if (gauge['status']['observed']['primary'] != undefined && gauge['status']['observed']['primary'] != null) {
						// ----------------------------------------------------------
						let od = gauge['status']['observed']['validTime'].split(/[^0-9]/);
						let observed_date_obj = new Date( od[0], od[1]-1, od[2]  );
						observed_date = '';
						// If it's in the future, then let's use the day name
						if (observed_date_obj >= today_obj) {
							observed_date = observed_date_obj.getDayNameShort();
						}
						// If it's today, say "today"
						else if (observed_date_obj.format('MMM D, YYYY') == today_obj.format('MMM D, YYYY')) {
							observed_date = 'Today';
						}
						// if it's in the past, use the date.
						else {
							observed_date = observed_date_obj.format('MMM D, YYYY');
						}
						observed = gauge['status']['observed']['primary'];
					}
					else {
						observed_date = 'N/A';
						observed = 'N/A';
					}

					// Only generate forecast data if there is actually a forceast
					if (
						gauge['status']['forecast']['primary'] != undefined &&
						gauge['status']['forecast']['primary'] != null &&
						gauge['status']['forecast']['primary'] != -999
					) {
						// ----------------------------------------------------------
						let fd = gauge['status']['forecast']['validTime'].split(/[^0-9]/);
						let forecast_date_obj = new Date( fd[0], fd[1]-1, fd[2]  );
						forecast_date = '';
						forecast_date_dif = (forecast_date_obj.getTime() - today_obj.getTime()) / (1000 * 3600 * 24);
						// If it's in the future, and within 7 days, then let's use the day name
						if (forecast_date_obj >= today_obj && forecast_date_dif < 7) {
							forecast_date = forecast_date_obj.getDayNameShort();
						}
						// If it's today, say "today"
						else if (forecast_date_obj.format('MMM D, YYYY') == today_obj.format('MMM D, YYYY')) {
							forecast_date = 'Today';
						}
						// if it's in the past, use the date.
						else {
							forecast_date = forecast_date_obj.format('MMM D, YYYY');
						}
						// ----------------------------------------------------------
						// let fi = gauge['fcstissunc'].split(/[^0-9]/);
						// let forecast_issue_obj = new Date( fi[0], fi[1]-1, fi[2] );
						// let forecast_issue_date = forecast_issue_obj.toDateString();
						// ----------------------------------------------------------
						forecast = gauge['status']['forecast']['primary'];
					}
					else {
						forecast_date = 'N/A'
						forecast = 'N/A';
						// let forecast_issue_date = null;
					}

					level_action = gauge['flood']['categories']['action']['stage'];
					level_minor = gauge['flood']['categories']['minor']['stage'];
					level_moderate = gauge['flood']['categories']['moderate']['stage'];
					level_major = gauge['flood']['categories']['major']['stage'];

					record = gauge['flood']['crests']['historic'][0]['stage'];
					let rd = gauge['flood']['crests']['historic'][0]['occurredTime'].split(/[^0-9]/);
					let record_date_obj = new Date( rd[0], rd[1]-1, rd[2] );
					record_date = `<span class="desktop-text">${record_date_obj.format('MMM DD,')}</span> ${record_date_obj.format('YYYY')}`;

					if (l == 'current') {
						status = catToInt(gauge['status']['observed']['floodCategory']) || 0;
					}
					else {
						fore_status = parseFloat(forecast);
						if (fore_status == null || fore_status == NaN) { status = 0; }
						else if (fore_status >= parseFloat(level_major)) { status = 5; }
						else if (fore_status >= parseFloat(level_moderate)) { status = 4; }
						else if (fore_status >= parseFloat(level_minor)) { status = 3; }
						else if (fore_status >= parseFloat(level_action)) { status = 2; }
						else { status = 1; }
					}


					let icon_color = '';
					switch (status) {
						case 0:
							icon_color = "#555"; // gray
							break;
						case 1:
							icon_color = "#66bd63"; // green
							break;
						case 2:
							icon_color = "#fed976"; // yellow
							break;
						case 3:
							icon_color = "#fd8d3c"; // orange
							break;
						case 4:
							icon_color = "#bd0026"; // red
							break;
						case 5:
							icon_color = "#5e4fa2";  // purple
							break;
					}

					let icon = L.JoshMarkers.icon({color: icon_color, size: 'm'});

					let marker = L.marker([ gauge['latitude'], gauge['longitude'] ], {icon: icon} );

					marker.bindPopup(`
						<h3>${river} at ${location}</h3>
						<table class="table__levels">
							<tr><th></th><th>Level</th><th>When</th></tr>
							<tr><td>Current</td><td>${observed}</td><td>${observed_date}</td></tr>
							<tr><td>Fore. max.</td><td>${forecast}</td><td>${forecast_date}</td></tr>
						</table>
						<table class="table__defs">
							<tr>
								<th>Nr. fld.</th>
								<th>Min.</th>
								<th>Mod.</th>
								<th>Maj.</th>
							</tr>
							<tr>
								<td>${level_action}</td>
								<td>${level_minor}</td>
								<td>${level_moderate}</td>
								<td>${level_major}</td>
							</tr>
						</table>
					`);

					marker_layers[l].addLayer(marker);

					let tableRow = `
						<tr>
		                    <td><div class="color-${status}"></div></td>
		                    <td>${location}</td>
		                    <td>${river}</td>
		                    <td>${observed}</td>
		                    <td>${forecast}</td>
		                    <td>${forecast_date}</td>
		                    <td>${record}</td>
		                    <td>${record_date}</td>
		                    <td>${level_action}</td>
		                    <td>${level_minor}</td>
		                    <td>${level_moderate}</td>
		                    <td>${level_major}</td>
						</tr>
					`;
					// Only insert the table rows ONCE, not twice.
					if (l == 'current') {
						document.querySelector('.interactive-table table tbody').insertAdjacentHTML('beforeend', tableRow);
					}

				}
			}
		}

		const current_view = document.querySelector('.toggle-button.active').dataset.value;

		map.addLayer(marker_layers[current_view]);

		pymChild.sendHeight();

	} // initialize()



	// 2024 Note: NOAA has a new version of their map available here: https://water.noaa.gov/wfo/lsx
	const gaugesUrl = '//graphics.stltoday.com/data/weather/river-gauges/local_river_gauges.json';

	Promise.all([
		fetch(gaugesUrl),
	])

	// Assemble the JSON from all responses into a single object for ease of processing.
	.then(function(responses) {
		// Get a JSON object from each of the responses
		return Promise.all(
			responses.map(function(response) {
				const contentType = response.headers.get('content-type');
				if (contentType && contentType.includes('text/csv')) {
					return response.text();
				}
				return response.json();
			})
		);
	})

	// Do stuff with the data
	.then( initialize )

	// Catch errors
	.catch(function(error) {
		console.log(error);
	});


	// This code is designed to allow multiple views, but for river-gauges there's just one view.
	// Refactored in 2024 to remove jQuery dependency.
	const views = ['0'];
	for (let v of views ) {
		document.querySelector(`.table-${v} .interactive-table-toggle`).addEventListener('click', function(e) {
			let $the_table = document.querySelector(`.table-${v} .interactive-table`);
			let $the_toggle = document.querySelector(`.table-${v} .interactive-table-toggle`);
			let $toggle_text = $the_toggle.innerText;

			if ( $the_table.classList.contains('hidden') ) {
				$the_toggle.innerText = $toggle_text.replace('Show','Hide');
				$the_table.classList.remove('hidden');
			}
			else {
				$the_toggle.innerText = $toggle_text.replace('Hide','Show');
				$the_table.classList.add('hidden');
			}
			pymChild.sendHeight();
			setTimeout(() => { pymChild.sendHeight(); }, 1000);
		}, false);
	}

	// Prepare to add click handlers for the toggle buttons
	const buttons = document.querySelectorAll('.toggle-button');
	for (const button of buttons) {

		// Add click handlers for the toggle buttons
		button.addEventListener('click', function(e) {

			// Iterate over all the toggle buttons and remove the active class
			for (const b of document.querySelectorAll('.toggle-button')) {
				b.classList.remove('active');
			}

			// Add the active class to the button that was clicked
			this.classList.add('active');

			// Update the view variable
			const view = this.dataset.value;
			const view_hidden = document.querySelector('.toggle-button:not(.active)').dataset.value;

			map.removeLayer(marker_layers[view_hidden]);
			map.addLayer(marker_layers[view]);

			// Update Pym height
			pymChild.sendHeight();

		}, false);

	}


})(); //app closure










