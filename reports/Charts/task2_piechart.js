

function displayTask2PieChart() {

    // Map is used for displaying percentage in legend.
    var tweetsData = new Map();
    tweetsData.set("Czech",  2513);
    tweetsData.set("Denmark",  5584);
    tweetsData.set("Estonia",  859);
    tweetsData.set("Finland",  2913);
    tweetsData.set("France",  118333);
    tweetsData.set("Hungary",  66);
    tweetsData.set("Netherlands",  12128);
    tweetsData.set("Norway",  608);
    tweetsData.set("Sweden",  11665);
  
    var dataset = [
        {label: "Czech", count: 2513},
        {label: "Denmark", count: 5584},
        {label: "Estonia", count: 859},
        {label: "Finland", count: 2913},
        {label: "France", count: 118333},
        {label: "Hungary", count: 66},
        {label: "Netherlands", count: 12128},
        {label: "Norway", count: 608},
        {label: "Sweden", count: 11665},
      ];
  
    var width = 600;
    var height = 400;
  
    var radius = Math.min(width, height) / 2.5;
  
    var legendRectSize = 14;
    var legendSpacing = 3;
  
    var color = d3.scaleOrdinal()
    .domain(tweetsData.keys())
    .range(d3.schemeSet2);
  
    var svg = d3.select('#task2_piechart')
      .append('svg') 
      .attr('width', width) 
      .attr('height', height) 
      .append('g') 
      .attr('transform', 'translate(' + (width / 3.5) + ',' + (height / 2) + ')');
  
    var arc = d3.arc()
      .innerRadius(0) 
      .outerRadius(radius);
  
    var pie = d3.pie() 
      .value(function(d) { return d.count; }) 
      .sort(null); 
  
  
    var tooltip = d3.select('#task2_piechart') 
      .append('div') 
      .attr('class', 'tooltip');
  
    tooltip.append('div')
      .attr('class', 'label'); 
  
    tooltip.append('div') 
      .attr('class', 'count'); 
  
    tooltip.append('div')
      .attr('class', 'percent');
  
    dataset.forEach(function(d) {
      d.count = +d.count;
      d.enabled = true;
    });
  
  
    var pathCount =0;
    var path = svg.selectAll('path')
      .data(pie(dataset)) 
      .enter()
      .append('path')
      .attr('d', arc) 
      .attr('fill', function(d) { return color(d.data.label); }) 
      .each(function(d) {
            var id = "path"+pathCount++;
            d3.select(this).attr("id", id); 
            var text = svg.append("text")
            .attr("x", 50)
            .attr("dy", 10)
            .attr("font-size", "14px");
  
            var total = d3.sum(dataset.map(function(d) { 
                return (d.enabled) ? d.count : 0;
                }));                                                      
            var percent = Math.round(1000 * d.data.count / total) / 10; 
                text.append("textPath")
                .attr("stroke","black")
                .attr("xlink:href","#"+id)
                .text(percent+"%");
          this._current - d; });
  
    path.on('mouseover', function(d) {
    var total = d3.sum(dataset.map(function(d) { 
      return (d.enabled) ? d.count : 0;
      }));                                                      
    var percent = Math.round(1000 * d.data.count / total) / 10; 
    tooltip.select('.label').html(d.data.label); 
    tooltip.select('.count').html(d.data.count); 
    tooltip.select('.percent').html(percent + '%'); 
    tooltip.style('display', 'block'); 
    });                                                           
  
    path.on('mouseout', function() { 
      tooltip.style('display', 'none');
    });
  
    path.on('mousemove', function(d) { 
      tooltip.style('top', (d3.event.layerY + 10) + 'px')
        .style('left', (d3.event.layerX + 10) + 'px'); 
      });
  
    var legend = svg.selectAll('.legend')
      .data(color.domain()) 
      .enter() 
      .append('g') 
      .attr('class', 'legend')
      .style("font-size", "14px")
      .attr('transform', function(d, i) {                   
        var height = legendRectSize + legendSpacing; 
        var offset =  height * color.domain().length / 2; 
        var horz = 13 * legendRectSize;
        var vert = i * height - offset; 
          return 'translate(' + horz + ',' + vert + ')'; 
      });
  
  
    legend.append('rect') 
      .attr('width', legendRectSize) 
      .attr('height', legendRectSize) 
      .style('fill', color) 
      .style('stroke', color) 
      .on('click', function(label) {
        var rect = d3.select(this); 
        var enabled = true; 
        var totalEnabled = d3.sum(dataset.map(function(d) { 
          return (d.enabled) ? 1 : 0; 
        }));
  
        if (rect.attr('class') === 'disabled') {
          rect.attr('class', ''); 
        } else { 
          if (totalEnabled < 2) return; 
          rect.attr('class', 'disabled'); 
          enabled = false; 
        }
  
        pie.value(function(d) { 
          if (d.label === label) d.enabled = enabled; 
            return (d.enabled) ? d.count : 0; 
        });
  
        path = path.data(pie(dataset)); 
  
        path.transition() 
          .duration(750) 
          .attrTween('d', function(d) {
            var interpolate = d3.interpolate(this._current, d); 
            this._current = interpolate(0); 
            return function(t) {
              return arc(interpolate(t));
            };
          });
      });
  
    legend.append('text')                                    
      .attr('x', legendRectSize + legendSpacing)
      .attr('y', legendRectSize - legendSpacing)
      .text(function(d) { 
          current_item_count = 0;
          var label = d;
          var total = d3.sum(dataset.map(function(d) {
            if (d.label === label) {
              current_item_count = d.count;
            }
            return (d.enabled) ? d.count : 0;
          }));                                          
          var percent = Math.round(1000 * current_item_count / total) / 10; 
          return d + " - " + percent +"%"; 
        }); 
  }