function displayTask2StackAreaChart() {

    csvData = "week,Czech,Denmark,Estonia,Finland,France,Hungary,Netherlands,Norway\n"
    csvData += "1,257,563,47,264,12266,6,873,55,1073\n";
    csvData += "2,344,640,103,361,15235,1,1570,74,1862\n";
    csvData += "3,230,495,112,255,8515,11,1107,52,1329\n";
    csvData += "4,247,526,105,250,13432,8,906,55,912\n";
    csvData += "5,272,501,71,268,10770,6,931,61,1114\n";
    csvData += "6,464,700,82,395,16817,5,1880,90,1482\n";
    csvData += "7,85,263,49,132,5394,4,781,29,560\n";
    csvData += "8,195,586,86,260,11552,10,1383,61,1183\n";
    csvData += "9,161,640,104,383,11090,9,1268,62,899\n";
    csvData += "10,258,670,100,345,13262,6,1429,69,1251\n";

    var margin = {top: 60, right: 150, bottom: 50, left: 60},
    width = 800 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

    var svg = d3.select("#task2_stackchart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform",
        "translate(" + margin.left + "," + margin.top + ")");

    
    var data = d3.csvParse(csvData);

    var keys = data.columns.slice(1)

  var color = d3.scaleOrdinal()
    .domain(keys)
    .range(d3.schemeSet2);

  var stackedData = d3.stack()
    .keys(keys)
    (data)


  var x = d3.scaleLinear()
    .domain(d3.extent(data, function(d) { return d.week; }))
    .range([ 0, width ]);
    
  var xAxis = svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x).ticks(5))

  svg.append("text")
      .attr("text-anchor", "end")
      .attr("x", width)
      .attr("y", height+40 )
      .text("Weeks");

  svg.append("text")
      .attr("text-anchor", "end")
      .attr("x", 0)
      .attr("y", -20 )
      .text("# of Tweets")
      .attr("text-anchor", "start")

  var y = d3.scaleLinear()
    .domain([0, 20000])
    .range([ height, 0 ]);
  svg.append("g")
    .call(d3.axisLeft(y).ticks(5))

  var clip = svg.append("defs").append("svg:clipPath")
      .attr("id", "clip")
      .append("svg:rect")
      .attr("width", width )
      .attr("height", height )
      .attr("x", 0)
      .attr("y", 0);

  var brush = d3.brushX()                 
      .extent( [ [0,0], [width, height] ] )
      .on("end", updateChart)

  var areaChart = svg.append('g')
    .attr("clip-path", "url(#clip)")

  var area = d3.area()
    .x(function(d) { return  x(d.data.week); })
    .y0(function(d) { return y(d[0]); })
    .y1(function(d) { return y(d[1]); })

  areaChart
    .selectAll("mylayers")
    .data(stackedData)
    .enter()
    .append("path")
      .attr("class", function(d) { return "myArea " + d.key })
      .style("fill", function(d) { return color(d.key); })
      .attr("d", area)


  areaChart
    .append("g")
      .attr("class", "brush")
      .call(brush);

  var idleTimeout
  function idled() { idleTimeout = null; }

  function updateChart() {

    extent = d3.event.selection

    if(!extent){
      if (!idleTimeout) return idleTimeout = setTimeout(idled, 350); 
      x.domain(d3.extent(data, function(d) { return d.week; }))
    }else{
      x.domain([ x.invert(extent[0]), x.invert(extent[1]) ])
      areaChart.select(".brush").call(brush.move, null) 
    }


    xAxis.transition().duration(1000).call(d3.axisBottom(x).ticks(5))
    areaChart
      .selectAll("path")
      .transition().duration(1000)
      .attr("d", area)
    }


    var highlight = function(d){
        d3.selectAll(".myArea").style("opacity", .2)
        d3.select("."+d).style("opacity", 1)
      }
  

      var noHighlight = function(d){
        d3.selectAll(".myArea").style("opacity", 1)
      }


    var size = 20
    svg.selectAll("myrect")
      .data(keys)
      .enter()
      .append("rect")
        .attr("x", 600)
        .attr("y", function(d,i){ return 10 + i*(size+5)}) 
        .attr("width", size)
        .attr("height", size)
        .style("fill", function(d){ return color(d)})
        .on("mouseover", highlight)
        .on("mouseleave", noHighlight)

    svg.selectAll("mylabels")
      .data(keys)
      .enter()
      .append("text")
        .attr("x", 600 + size*1.4)
        .attr("y", function(d,i){ return 10 + i*(size+5) + (size/2)})
        .style("fill", function(d){ return color(d)})
        .text(function(d){ return d})
        .attr("text-anchor", "left")
        .style("alignment-baseline", "middle")
        .on("mouseover", highlight)
        .on("mouseleave", noHighlight)
        .attr("font-size","14px")
}
