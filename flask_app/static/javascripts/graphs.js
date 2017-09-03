$('.bar_chart').ready(function () {
  $.ajax({
    url: '/likes',
    error: function () {
      $('.bar_processing_div').hide();
      $('.bar_error_div').show()
    },
    success: function (data) {
      $('.bar_processing_div').hide();
      try {
        var bucket_data = data['aggregations']['likes_by_keyword']['buckets'];

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

        bucket_data.forEach(function (d) {
          d.avg_likes = +d["average_likes"]["value"];
          d.avg_dislikes = +d["average_dislikes"]["value"];
        });

        // scale the range of the data
        x.domain(bucket_data.map(function (d) {
          return d.key;
        }));
        y.domain([0, d3.max(bucket_data, function (d) {
          return d.avg_likes;
        })]);

        // add axis
        svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", "-.55em")
        .attr("transform", "rotate(-90)");

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
        .attr("x", function (d) {
          return x(d.key);
        })
        .attr("width", x.rangeBand())
        .attr("y", function (d) {
          return y(d.avg_likes);
        })
        .attr("height", function (d) {
          return height - y(d.avg_likes);
        });

        $('.bar_data_div').show();

      }
      catch
          (exception) {
        console.error(exception);
        $('.bar_data_div').hide();
        $('.bar_error_div').show();
      }
    },
    type: 'GET'
  });
});

$('.pie_chart').ready(function () {
  $.ajax({
    url: '/views_range',
    error: function () {
      $('.pie_processing_div').hide();
      $('.pie_error_div').show()
    },
    success: function (data) {
      $('.pie_processing_div').hide();
      try {
        var bucket_data = data['aggregations']['view_ranges']['buckets'];

        var w = 400;
        var h = 300;
        var r = h / 2;
        var aColor = [
          '#CF5656',
          '#EC8080',
          '#FFC4C4',
          '#FFDDDD',
          '#FFECDD',
          '#FFDFC4',
          '#ECB180',
          '#CF8D56',
          '#45A545',
          '#66BD66',
          '#ACDFAC',
          '#CCECCC',
          '#347C7C',
          '#4D8E8E',
          '#BCD9D9'
        ];

        var vis = d3.select('.pie_data_div')
        .append("svg:svg")
        .data(bucket_data)
        .attr("width", w).attr("height", h).append("svg:g").attr(
            "transform", "translate(" + r + "," + r + ")");

        var pie = d3.layout.pie().value(function (d) {
          return d.doc_count;
        });

// Declare an arc generator function
        var arc = d3.svg.arc().outerRadius(r);

// Select paths, use arc generator to draw
        var arcs = vis.selectAll("g.slice").data(
            pie(bucket_data)).enter().append(
            "svg:g").attr("class", "slice");
        arcs.append("svg:path")
        .attr("fill", function (d, i) {
          return aColor[i];
        })
        .attr("d", function (d) {
          return arc(d);
        })
        ;

// Add the text
        arcs.append("svg:text")
        .attr("transform", function (d) {
              d.innerRadius = 100;
              /* Distance of label to the center*/
              d.outerRadius = r;
              return "translate(" + arc.centroid(d) + ")";
            }
        )
        .attr("text-anchor", "middle")
        .text(function (d, i) {
          return bucket_data[i].key;
        });

        var legendG = vis.selectAll(".legend")
        .data(pie(bucket_data))
        .enter().append("g")
        .attr("transform", function (d, i) {
          return "translate(" + (w - 50) + "," + (i + 15) + ")"; // place each legend on the right and bump each one down 15 pixels
        })
        .attr("class", "legend");

        legendG.append("rect") // make a matching color rect
        .attr("width", 10)
        .attr("height", 10)
        .attr("fill", function (d, i) {
          return aColor[i];
        });

        legendG.append("text") // add the text
        .text(function (d) {
          return d.key;
        })
        .style("font-size", 12)
        .style("font-color", "#000")
        .attr("y", 10)
        .attr("x", 11);

        $('.pie_data_div').show();
      }
      catch
          (exception) {
        console.error(exception);
        $('.pie_data_div').hide();
        $('.pie_error_div').show();
      }
    },
    type: 'GET'
  });
});

$('.word_cloud').ready(function () {

  $.ajax({
    url: '/tags',
    error: function () {
      $('.cloud_processing_div').hide();
      $('.cloud_error_div').show()
    },
    success: function (data) {
      $('.cloud_processing_div').hide();
      try {
        var bucket_data = data['aggregations']['doc_count']['buckets'];

        var word_count = {};

        bucket_data.forEach(function (d) {
          word_count[d["key"]] = d["doc_count"];
        });

        var svg_location = ".cloud_data_div";
        var width = 600;
        var height = 400;

        var fill = d3.scale.category20();

        var word_entries = d3.entries(word_count);

        var xScale = d3.scale.linear()
        .domain([0, d3.max(word_entries, function (d) {
          return d.value;
        })
        ])
        .range([10, 100]);

        d3.layout.cloud().size([width, height])
        .timeInterval(20)
        .words(word_entries)
        .fontSize(function (d) {
          return xScale(+d.value);
        })
        .text(function (d) {
          return d.key;
        })
        .rotate(function () {
          return ~~(Math.random() * 2) * 90;
        })
        .font("Impact")
        .on("end", draw)
        .start();

        function draw(words) {
          d3.select(svg_location).append("svg")
          .attr("width", width)
          .attr("height", height)
          .append("g")
          .attr("transform", "translate(" + [width >> 1, height >> 1] + ")")
          .selectAll("text")
          .data(words)
          .enter().append("text")
          .style("font-size", function (d) {
            return xScale(d.value) + "px";
          })
          .style("font-family", "Impact")
          .style("fill", function (d, i) {
            return fill(i);
          })
          .attr("text-anchor", "middle")
          .attr("transform", function (d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
          })
          .text(function (d) {
            return d.key;
          });
        }

        d3.layout.cloud().stop();

        $('.cloud_data_div').show();
      }
      catch
          (exception) {
        console.error(exception);
        $('.cloud_data_div').hide();
        $('.cloud_error_div').show();
      }
    },
    type: 'GET'
  });

});

$('.histogram').ready(function () {

  $.ajax({
    url: '/publish_dates',
    error: function () {
      $('.histogram_processing_div').hide();
      $('.histogram_error_div').show()
    },
    success: function (data) {
      $('.histogram_processing_div').hide();
      try {
        var bucket_data = data['aggregations']['videos_publish_interval']['buckets'];
        console.log(bucket_data);

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
        var svg = d3.select(".histogram_data_div").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

        bucket_data.forEach(function (d) {
          d.count = +d["doc_count"];
        });

        // scale the range of the data
        x.domain(bucket_data.map(function (d) {
          return d.key_as_string;
        }));
        y.domain([0, d3.max(bucket_data, function (d) {
          return d.count;
        })]);

        // add axis
        svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", "-.55em")
        .attr("transform", "rotate(-90)");

        svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 5)
        .attr("dy", ".71em")
        .style("text-anchor", "end");

        // Add bar chart
        svg.selectAll(".histogram_data_div")
        .data(bucket_data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function (d) {
          return x(d.key_as_string);
        })
        .attr("width", x.rangeBand())
        .attr("y", function (d) {
          return y(d.count);
        })
        .attr("height", function (d) {
          return height - y(d.count);
        });


        $('.histogram_data_div').show();
      }
      catch
          (exception) {
        console.error(exception);
        $('.histogram_data_div').hide();
        $('.histogram_error_div').show();
      }
    },
    type: 'GET'
  });

});

$(document).ready(function () {
  console.log("page loaded");
});