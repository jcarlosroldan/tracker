function getJSON(url, success = console.log, error = console.log, method = 'GET') {
	var req = new XMLHttpRequest()
	req.open(method, url, true)
	req.onload = function() {
		if (req.status == 200) {
			success(JSON.parse(req.responseText))
		} else {
			error(req.responseText)
		}
	}
	req.onerror = function() {
		error(req.responseText)
	}
	req.send()
}

window.onload = function() {
/*
// set the dimensions and margins of the graph
var margin = {top: 0, right: 25, bottom: 30, left: 40},
	width = 750 - margin.left - margin.right,
	height = 550 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select(".session-starts")
.append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
.append("g")
	.attr("transform",
		"translate(" + margin.left + "," + margin.top + ")");

//Read the data
d3.json("/api/session-starts.json", function(data) {

	// Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
	var weekDays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
	var hours = []
	let padded = (h) => ('0' + h).slice(-2)
	for (var h = 23; h >= 0; h -= 1) hours.push(padded(h))

	// Build X scales and axis:
	var x = d3.scaleBand()
	.range([0, width ])
	.domain(weekDays)
	.padding(0.2);
	svg.append("g")
		.attr("class", 'axis')
	.attr("transform", "translate(0," + height + ")")
	.call(d3.axisBottom(x).tickSize(0))
	.select(".domain").remove()

	// Build Y scales and axis:
	var y = d3.scaleBand()
	.range([ height, 0 ])
	.domain(hours)
	.padding(0.1);
	svg.append("g")
	.attr("class", "axis")
	.call(d3.axisLeft(y).tickSize(5))
	.select(".domain").remove()

	// Build color scale
	var myColor = d3.scaleSequential()
	.interpolator(d3.interpolateCool)
	.domain([1,100])

	// create a tooltip
	var tooltip = d3.select(".session-starts")
	.append("div")
	.style("opacity", 0)
	.attr("class", "tooltip")

	// Three function that change the tooltip when user hover / move / leave a cell
	var mouseover = function(d) {
	tooltip.html(`Started ${d[2]} time${d[2] == 1?'':'s'} on ${weekDays[d[0]]} ${d[1]}:00 - ${(d[1] + 1) % 24}:00`)
	tooltip.style("opacity", 1)

	}
	var mouseleave = function(d) {
	tooltip.style("opacity", 0)
	}

	// add the squares
	svg.selectAll()
	.data(data, function(d) {return d[0]+':'+d[1];})
	.enter()
	.append("rect")
		.attr("x", function(d) { return x(weekDays[d[0]])})
		.attr("y", function(d) { return y(padded(d[1])) })
		.attr("width", x.bandwidth() )
		.attr("height", y.bandwidth() )
		.style("fill", function(d) { return myColor(d[2])} )
	.on("mouseover", mouseover)
	.on("mouseleave", mouseleave)
})*/

getJSON('/api/session-starts.json', function(data) {
Highcharts.chart('session-starts', {
		credits: 'false',
		options : { scales : {gridLines : { display : false } } },
		chart: {
				type: 'heatmap',
				marginTop: 1,
				marginBottom: 26,
				plotBorderWidth: 0,
				backgroundColor: 'none'
		},
		title: {text: ''},
		xAxis: {
			categories: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		},
		yAxis: {
			categories: Array.from({length: 24}, (v, i) => ('0' + i).slice(-2)),
			title: null,
			gridLineColor: '#383a4'
		},
		colorAxis: {
				min: 0,
				stops: [
            [0, '#2a3235'],
            [0.75, '#1998c5'],
            [1, '#14acb6']
        ]
		},
		legend: {
				align: 'right',
				layout: 'vertical',
				margin: 0,
				verticalAlign: 'top',
				y: 25,
				symbolHeight: 280
		},
		tooltip: false,
		series: [{data: data}]
})})

}