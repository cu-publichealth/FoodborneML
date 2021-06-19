class Histogram{
    constructor(id, margin, height, width, numberOfBins, numberOfTicks){
        this.svg = d3.select(id)
          .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");

        this.yAxis = this.svg.append("g");
        this.xAxis = this.svg.append("g").attr("transform", "translate(0," + height + ")");
        this.height = height;
        this.width = width;
        this.numberOfBins = numberOfBins;
        this.numberOfTicks = numberOfTicks;
    }

    changeHistogram(values, startDate, endDate){
        var x = d3.scaleTime().domain([startDate, endDate]).range([0, this.width]);
        var y = d3.scaleLinear().range([this.height, 0]);

        var histogram = d3.histogram()
            .value(function(d) { return d; })   // I need to give the vector of value
            .domain(x.domain())  // then the domain of the graphic
            .thresholds(x.ticks(this.numberOfBins)); // then the numbers of bins

        var bins = histogram(values);

        y.domain([0, d3.max(bins, function(d) { return d.length; })]);   // d3.hist has to be called before the Y axis obviously
        this.yAxis.transition()
            .duration(1000)
            .call(d3.axisLeft(y).ticks(this.numberOfTicks));

        this.xAxis.transition().duration(1000).call(d3.axisBottom(x).ticks(this.numberOfTicks))

        var u = this.svg.selectAll("rect")
                .data(bins);

    // Manage the existing bars and eventually the new ones:
        u
        .enter()
        .append("rect") // Add a new rect for each new elements
        .merge(u) // get the already existing elements as well
        .transition() // and apply changes to all of them
        .duration(1000)
          .attr("x", 1)
          .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; })
          .attr("width", function(d) { return Math.max(x(d.x1) - x(d.x0) -1, 0); })
          .attr("height", function(d) { return height - y(d.length); })
          .style("fill", "blue")


    // If less bar in the new histogram, I delete the ones not in use anymore
         u.exit().remove()
    }

}