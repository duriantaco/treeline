import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface CodeMetricsGraphsProps {
  metrics: any;
  codeSmells: any[];
  className?: string;
}

const CodeMetricsGraphs: React.FC<CodeMetricsGraphsProps> = ({ 
  metrics, 
  codeSmells,
  className = '' 
}) => {
  const donutChartRef = useRef<SVGSVGElement>(null);
  const barChartRef = useRef<SVGSVGElement>(null);
  const radarChartRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (metrics && codeSmells) {
      renderDonutChart();
      renderBarChart();
      renderRadarChart();
    }
  }, [metrics, codeSmells]);
  
  const renderDonutChart = () => {
    if (!donutChartRef.current) return;
    
    d3.select(donutChartRef.current).selectAll('*').remove();
    
    const width = 300;
    const height = 300;
    const margin = 40;
    
    const radius = Math.min(width, height) / 2 - margin;
    
    const svg = d3.select(donutChartRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);
    
    const issueCategories: { [key: string]: number } = {};
    
    codeSmells.forEach(smell => {
      let category = 'Other';
      
      if (typeof smell === 'string') {
        const match = smell.match(/^\[([^\]]+)\]/);
        if (match) category = match[1];
      } else if (smell.category) {
        category = smell.category;
      } else if (smell.message && smell.message.includes('complexity')) {
        category = 'Complexity';
      } else if (smell.message && smell.message.includes('security')) {
        category = 'Security';
      }
      
      issueCategories[category] = (issueCategories[category] || 0) + 1;
    });
    
    const data = Object.entries(issueCategories).map(([name, value]) => ({name, value}));
    
    const color = d3.scaleOrdinal()
      .domain(data.map(d => d.name))
      .range([
        '#ef4444', // red (security)
        '#f59e0b', // amber (complexity)
        '#3b82f6', // blue (style)
        '#10b981', // emerald (duplication)
        '#8b5cf6', // violet (other)
        '#ec4899', // pink
        '#6366f1'  // indigo
      ]);
    
    const pie = d3.pie<any>()
      .sort(null)
      .value(d => d.value);
    
    const arc = d3.arc()
      .innerRadius(radius * 0.5)
      .outerRadius(radius * 0.8);
    
    const outerArc = d3.arc()
      .innerRadius(radius * 0.9)
      .outerRadius(radius * 0.9);
    
    const arcs = svg.selectAll('allSlices')
      .data(pie(data))
      .enter()
      .append('path')
      .attr('d', arc as any)
      .attr('fill', d => color(d.data.name) as string)
      .attr('stroke', 'white')
      .style('stroke-width', '2px')
      .style('opacity', 0.7);
    
    arcs.append('title')
        .text(d => `${d.data.name}: ${d.data.value} issues (${Math.round(d.data.value/codeSmells.length*100)}%)`);

    
    svg.selectAll('allPolylines')
      .data(pie(data))
      .enter()
      .append('polyline')
      .attr('stroke', 'black')
      .style('fill', 'none')
      .attr('stroke-width', 1)
      .attr('points', function(d) {
        const posA = arc.centroid(d as any);
        const posB = outerArc.centroid(d as any);
        const posC = outerArc.centroid(d as any);
        posC[0] = radius * 0.95 * (d.startAngle + (d.endAngle - d.startAngle) / 2 < Math.PI ? 1 : -1);
        return `${posA[0]},${posA[1]} ${posB[0]},${posB[1]} ${posC[0]},${posC[1]}`;
      });
    
    svg.selectAll('allLabels')
      .data(pie(data))
      .enter()
      .append('text')
      .text(d => `${d.data.name} (${d.data.value})`)
      .attr('transform', function(d) {
        const pos = outerArc.centroid(d as any);
        pos[0] = radius * 0.99 * (d.startAngle + (d.endAngle - d.startAngle) / 2 < Math.PI ? 1 : -1);
        return `translate(${pos})`;
      })
      .style('text-anchor', d => (d.startAngle + (d.endAngle - d.startAngle) / 2 < Math.PI ? 'start' : 'end'))
      .style('font-size', '12px');
    
    svg.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .text(`${codeSmells.length} Issues`);
  };
  
  const renderBarChart = () => {
    if (!barChartRef.current || !metrics) return;
    
    d3.select(barChartRef.current).selectAll('*').remove();
    
    const width = 450;
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 70, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    const svg = d3.select(barChartRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const metricsToShow = [
      { key: 'complexity', label: 'Complexity', threshold: 10 },
      { key: 'cognitive_complexity', label: 'Cognitive', threshold: 15 },
      { key: 'nested_depth', label: 'Nesting', threshold: 4 },
      { key: 'params', label: 'Parameters', threshold: 5 },
      { key: 'lines', label: 'Lines', threshold: 100, scale: 0.1 }
    ];
    
    const data = metricsToShow
      .filter(m => metrics[m.key] !== undefined)
      .map(m => ({
        name: m.label,
        value: m.scale ? metrics[m.key] * m.scale : metrics[m.key],
        originalValue: metrics[m.key],
        threshold: m.scale ? m.threshold * m.scale : m.threshold
      }));
    
    const x = d3.scaleBand()
      .domain(data.map(d => d.name))
      .range([0, innerWidth])
      .padding(0.3);
    
    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => Math.max(d.value, d.threshold)) as number * 1.1])
      .range([innerHeight, 0]);
    
    svg.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');
    
    svg.append('g')
      .call(d3.axisLeft(y));
    
    svg.selectAll('threshold-lines')
      .data(data)
      .enter()
      .append('line')
      .attr('x1', d => (x(d.name) || 0))
      .attr('x2', d => (x(d.name) || 0) + x.bandwidth())
      .attr('y1', d => y(d.threshold))
      .attr('y2', d => y(d.threshold))
      .attr('stroke', '#ef4444')
      .attr('stroke-dasharray', '5,5')
      .attr('stroke-width', 1);
    
    svg.selectAll('bars')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => x(d.name) || 0)
      .attr('y', d => y(d.value))
      .attr('width', x.bandwidth())
      .attr('height', d => innerHeight - y(d.value))
      .attr('fill', d => d.value > d.threshold ? '#ef4444' : '#3b82f6')
      .on('mouseover', function(_, d) {
        d3.select(this).attr('fill-opacity', 0.7);
        
        svg.append('text')
          .attr('class', 'tooltip-text')
          .attr('x', (x(d.name) || 0) + x.bandwidth() / 2)
          .attr('y', y(d.value) - 15)
          .attr('text-anchor', 'middle')
          .style('font-size', '12px')
          .style('font-weight', 'bold')
          .text(`${d.name}: ${d.originalValue}${d.value > d.threshold ? ' ⚠️' : ''}`);
      })
      .on('mouseout', function() {
        d3.select(this).attr('fill-opacity', 1);
        svg.selectAll('.tooltip-text').remove();
      });
      
    svg.selectAll('bar-values')
      .data(data)
      .enter()
      .append('text')
      .attr('x', d => (x(d.name) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.value) - 5)
      .attr('text-anchor', 'middle')
      .text(d => d.originalValue)
      .style('font-size', '12px');
    
    svg.append('text')
      .attr('x', innerWidth / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text('Key Metrics vs. Thresholds');
  };
  
  const renderRadarChart = () => {
    if (!radarChartRef.current || !metrics) return;
    
    d3.select(radarChartRef.current).selectAll('*').remove();
    
    const width = 350;
    const height = 350;
    const margin = 60;
    
    const svg = d3.select(radarChartRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width/2},${height/2})`);
    
    const radius = Math.min(width, height) / 2 - margin;
    
    const metricsToShow = [
      { key: 'complexity', label: 'Complexity', max: 20 },
      { key: 'cognitive_complexity', label: 'Cognitive Complexity', max: 25 },
      { key: 'nested_depth', label: 'Nesting Depth', max: 8 },
      { key: 'params', label: 'Parameters', max: 10 },
      { key: 'functions', label: 'Functions', max: 20 }
    ].filter(m => metrics[m.key] !== undefined);
    
    const data = [
      metricsToShow.map(m => ({
        axis: m.label,
        value: Math.min(1, metrics[m.key] / m.max)
      }))
    ];
    
    const allAxis = data[0].map(i => i.axis);
    const total = allAxis.length;
    const angleSlice = Math.PI * 2 / total;
    
    const rScale = d3.scaleLinear()
      .range([0, radius])
      .domain([0, 1]);
    
    const axisGrid = svg.append('g').attr('class', 'axis-grid');
    
    axisGrid.selectAll('.axis-line')
      .data(d3.range(1, 6))
      .enter()
      .append('circle')
      .attr('cx', 0)
      .attr('cy', 0)
      .attr('r', d => radius / 5 * d)
      .style('fill', 'none')
      .style('stroke', 'gray')
      .style('stroke-dasharray', '4,4')
      .style('opacity', 0.5);
    
    const axis = axisGrid.selectAll('.axis')
      .data(allAxis)
      .enter()
      .append('g')
      .attr('class', 'axis');
    
    axis.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', (_, i) => rScale(1.1) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y2', (_, i) => rScale(1.1) * Math.sin(angleSlice * i - Math.PI / 2))
      .style('stroke', 'gray')
      .style('stroke-width', '1px');
    
    axis.append('text')
      .attr('class', 'legend')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('x', (_, i) => rScale(1.15) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (_, i) => rScale(1.15) * Math.sin(angleSlice * i - Math.PI / 2))
      .text(d => d)
      .style('font-size', '10px');
    
    const radarLine = d3.lineRadial<{axis: string, value: number}>()
      .curve(d3.curveLinearClosed)
      .radius(d => rScale(d.value))
      .angle((_, i) => i * angleSlice);
    
    const blobWrapper = svg.selectAll('.radar-wrapper')
      .data(data)
      .enter()
      .append('g')
      .attr('class', 'radar-wrapper');
    
    blobWrapper
      .append('path')
      .attr('class', 'radar-area')
      .attr('d', d => radarLine(d) as string)
      .style('fill', '#3b82f6')
      .style('fill-opacity', 0.5)
      .style('stroke', '#3b82f6')
      .style('stroke-width', '1px');
    
    blobWrapper.selectAll('.radar-circle')
      .data(d => d)
      .enter()
      .append('circle')
      .attr('class', 'radar-circle')
      .attr('r', 5)
      .attr('cx', (d, i) => rScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (d, i) => rScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2))
      .style('fill', '#3b82f6')
      .style('stroke', 'none');
    
    svg.append('text')
      .attr('x', 0)
      .attr('y', -radius - 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text('Complexity Radar');
  };
  
  return (
    <div className={`code-metrics-graphs ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-center">Code Issues by Category</h3>
          <div className="flex justify-center">
            <svg ref={donutChartRef}></svg>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-center">Complexity Profile</h3>
          <div className="flex justify-center">
            <svg ref={radarChartRef}></svg>
          </div>
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow mb-8">
        <h3 className="text-lg font-semibold mb-4 text-center">Metrics vs Thresholds</h3>
        <div className="flex justify-center">
          <svg ref={barChartRef}></svg>
        </div>
      </div>
    </div>
  );
};

export default CodeMetricsGraphs;