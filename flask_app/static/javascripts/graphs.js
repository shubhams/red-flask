$('.bar_chart').ready(function () {
  $.ajax({
    url: 'https://blooming-escarpment-84898.herokuapp.com/likes',
    error: function () {
      $('.bar_processing_div').hide();
      $('.bar_error_div').show()
    },
    success: function (data) {
      $('.bar_processing_div').hide();
      if (data['_shards']['successful'] > 0) {
        $('.bar_data_div').show();

        var bucket_data = data['aggregations']['likes_by_keyword']['buckets'];
        console.log(bucket_data);

        // d3.select(".bar_data_div")
        // .selectAll("div")
        // .data(bucket_data)
        // .enter().append("div")
        // .style("width", function (d) {
        //   return d['average_dislikes']['value'] + "px";
        // })
        // .text(function (d) {
        //   return d['average_dislikes']['value'];
        // });




        // set the dimensions of the canvas
        var margin = {top: 20, right: 20, bottom: 70, left: 40},
            width = 600 - margin.left - margin.right,
            height = 300 - margin.top - margin.bottom;


// set the ranges
        var x = d3.scale.ordinal().rangeRoundBands([0, width], .05);

        var y = d3.scale.linear().range([height, 0]);

// define the axis
        var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");


        var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10);


// add the SVG element
        var svg = d3.select(".bar_data_div").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");


        bucket_data.forEach(function(d) {
          d.avg_likes = +d["average_likes"]["value"];
          d.avg_dislikes = +d["average_dislikes"]["value"];
          console.log(d);
        });

        // scale the range of the data
        x.domain(bucket_data.map(function(d) { return d.key; }));
        y.domain([0, d3.max(bucket_data, function(d) { return d.avg_likes; })]);

        // add axis
        svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", "-.55em")
        .attr("transform", "rotate(-90)" );

        svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 5)
        .attr("dy", ".71em")
        .style("text-anchor", "end");

        // Add bar chart
        svg.selectAll(".bar_data_div")
        .data(bucket_data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return x(d.key); })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d.avg_likes); })
        .attr("height", function(d) { return height - y(d.avg_likes); });








      } else {
        $('.bar_error_div').show();
      }
    },
    type: 'GET'
  });
});

$(document).ready(function () {
  console.log("page loaded");
});