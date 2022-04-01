import * as d3 from 'd3'
import * as topojson from 'topojson'

(function () {
  const margin = {
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  }

  // const width = 400 - margin.left - margin.right
  // const height = 800 - margin.top - margin.bottom

  var width = 1160;
var height = 700;

  //
  const svg = d3
    .select('#chart')
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')

  //       // The svg
  // var svg2 = d3.select("chart2"),
  //     width = +svg.attr("width"),
  //     height = +svg.attr("height");
  //
  // Map and projection
  var projection = d3.geoAlbersUsa()
    .scale(800)
    .translate([width / 2, height / 2])

  var path = d3.geoPath()
    .projection(projection)

  //
  //
  //
  d3.queue()
    .defer(d3.json, '/data/us.json')
    .await(ready)
  //
  // d3.json('/data/us.json', (row) => {
  //    console.log(row)
  //    return row
  //  }).then(ready)

  function ready (error, data) {
    if (error) {
      console.log(error.stack)
    }
    d3.select('#step-0').on('stepin', function () {
      console.log(data)
      var states = topojson.feature(data, data.objects.states).features
      console.log(states)

      svg.selectAll('.state')
        .data(states)
        .enter().append('path')
        .attr('class', 'state')
        .attr('d', path)
    })
  }
})()
