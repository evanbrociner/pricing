(function () {
  const margin = {
    top: 40,
    right: 30,
    bottom: 20,
    left: 40,
  };

  const width = 400 - margin.left - margin.right;
  const height = 500 - margin.top - margin.bottom;

  const svg = d3
    .select("#chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");



          // The svg
    var svg2 = d3.select("chart2"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    // Map and projection
    var projection = d3.geoMercator()
        .center([2, 47])                // GPS of location to zoom on
        .scale(1020)                       // This is like the zoom
        .translate([ width/2, height/2 ])



  d3.csv("/data/hospitals_per_state.csv", (row) => {
    row.sum= parseInt(row.sum)

    console.log(row);
    return row;
  }).then(ready);

  function ready(datapoints) {
    d3.select("#step-0").on("stepin", function () {
      let allData = datapoints.filter((d) => d);


            // X axis
            const x = d3
              .scaleBand()
              .range([0, width])
              .domain(allData.map((d) => d.state))
              .padding(0.2);
            svg
              .append("g")
              .attr("transform", `translate(0, ${height})`)
              .call(d3.axisBottom(x))
              .selectAll("text")
              .attr("transform", "translate(-10,0)rotate(-45)")
              .style("text-anchor", "end");

            // Add Y axis
            const y = d3.scaleLinear().domain([0, 300]).range([height, 0]);
            svg.append("g").call(d3.axisLeft(y));

            svg
              .selectAll("chart")
              .data(allData, (d) => d.sum)
              .join("rect")
              .attr("x", (d) => x(d.state))
              .attr("y", (d) => y(d.sum))
              .attr("width", x.bandwidth())
              .attr("height", (d) => height - y(d.sum))
              .attr("fill", "#69b3a2");

    });

    d3.select("#step-1").on("stepin", function () {
      let allData = datapoints.filter((d) => d.sum > 50);

      // X axis
      const x = d3
        .scaleBand()
        .range([0, width])
        .domain(allData.map((d) => d.state))
        .padding(0.2);

      svg2
        .append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)")
        .style("text-anchor", "end");

      // Add Y axis
      const y = d3.scaleLinear().domain([0, 300]).range([height, 0]);
      svg.append("g").call(d3.axisLeft(y));

      svg2
        .selectAll("chart2")
        .data(allData, (d) => d.sum)
        .join("rect")
        .attr("x", (d) => x(d.state))
        .attr("y", (d) => y(d.sum))
        .attr("width", x.bandwidth())
        .attr("height", (d) => height - y(d.sum))
        .attr("fill", "#69b3a2");
    });

    d3.select("#step-2").on("stepin", function () {
    });

  }
})();
