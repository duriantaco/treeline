import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ComplexityTimelineProps {
  currentComplexity: number;
  currentCognitiveComplexity: number;
  currentNestedDepth?: number;
  className?: string;
}

const ComplexityTimeline: React.FC<ComplexityTimelineProps> = ({ 
  currentComplexity, 
  currentCognitiveComplexity,
  currentNestedDepth,
  className = ''
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!svgRef.current) return;
    
    d3.select(svgRef.current).selectAll('*').remove();
    
    const margin = { top: 30, right: 80, bottom: 50, left: 60 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const refactoringSteps = 5;
    const complexityData = [];
    const cognitiveData = [];
    const nestedDepthData = [];
    
    for (let i = 0; i <= refactoringSteps; i++) {
      const reductionFactor = 1 - (i * 0.15); 
      
      complexityData.push({
        step: i,
        value: Math.max(2, Math.round(currentComplexity * reductionFactor)),
        metric: 'complexity'
      });
      
      cognitiveData.push({
        step: i,
        value: Math.max(1, Math.round(currentCognitiveComplexity * reductionFactor)),
        metric: 'cognitive'
      });
      
      if (currentNestedDepth) {
        nestedDepthData.push({
          step: i,
          value: Math.max(1, Math.round(currentNestedDepth * reductionFactor)),
          metric: 'depth'
        });
      }
    }
    
    const allData = [...complexityData, ...cognitiveData];
    if (currentNestedDepth) allData.push(...nestedDepthData);
    
    const x = d3.scaleLinear()
      .domain([0, refactoringSteps])
      .range([0, width]);
      
    const y = d3.scaleLinear()
      .domain([0, d3.max(allData, d => d.value) || 0])
      .nice()
      .range([height, 0]);
    
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(refactoringSteps + 1).tickFormat(d => `Step ${d}`));
    
    svg.append('g')
      .call(d3.axisLeft(y));
    
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', height + 40)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '500')
      .text('Refactoring Steps');
    
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -40)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '500')
      .text('Complexity Score');
    
    svg.append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', y(10))
      .attr('y2', y(10))
      .attr('stroke', '#ef4444')
      .attr('stroke-dasharray', '5,5')
      .attr('stroke-width', 1);
    
    svg.append('text')
      .attr('x', width)
      .attr('y', y(10) - 5)
      .attr('text-anchor', 'end')
      .attr('fill', '#ef4444')
      .attr('font-size', '12px')
      .text('Complexity Threshold (10)');
    
    svg.append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', y(15))
      .attr('y2', y(15))
      .attr('stroke', '#f59e0b')
      .attr('stroke-dasharray', '5,5')
      .attr('stroke-width', 1);
    
    svg.append('text')
      .attr('x', width)
      .attr('y', y(15) - 5)
      .attr('text-anchor', 'end')
      .attr('fill', '#f59e0b')
      .attr('font-size', '12px')
      .text('Cognitive Complexity Threshold (15)');
    
    const complexityLine = d3.line<{step: number, value: number}>()
      .x(d => x(d.step))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);
    
    const cognitiveComplexityLine = d3.line<{step: number, value: number}>()
      .x(d => x(d.step))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);
    
    const nestedDepthLine = d3.line<{step: number, value: number}>()
      .x(d => x(d.step))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);
    
    svg.append('path')
      .datum(complexityData)
      .attr('fill', 'none')
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 2)
      .attr('d', complexityLine);
    
    svg.append('path')
      .datum(cognitiveData)
      .attr('fill', 'none')
      .attr('stroke', '#f59e0b')
      .attr('stroke-width', 2)
      .attr('d', cognitiveComplexityLine);
    
    if (currentNestedDepth) {
      svg.append('path')
        .datum(nestedDepthData)
        .attr('fill', 'none')
        .attr('stroke', '#10b981')
        .attr('stroke-width', 2)
        .attr('d', nestedDepthLine);
    }
    
    svg.selectAll('.complexity-dot')
      .data(complexityData)
      .enter()
      .append('circle')
      .attr('class', 'complexity-dot')
      .attr('cx', d => x(d.step))
      .attr('cy', d => y(d.value))
      .attr('r', 5)
      .attr('fill', '#3b82f6');
    
    svg.selectAll('.cognitive-dot')
      .data(cognitiveData)
      .enter()
      .append('circle')
      .attr('class', 'cognitive-dot')
      .attr('cx', d => x(d.step))
      .attr('cy', d => y(d.value))
      .attr('r', 5)
      .attr('fill', '#f59e0b');
    
    if (currentNestedDepth) {
      svg.selectAll('.depth-dot')
        .data(nestedDepthData)
        .enter()
        .append('circle')
        .attr('class', 'depth-dot')
        .attr('cx', d => x(d.step))
        .attr('cy', d => y(d.value))
        .attr('r', 5)
        .attr('fill', '#10b981');
    }
    
    svg.selectAll('.complexity-label')
      .data(complexityData)
      .enter()
      .append('text')
      .attr('class', 'complexity-label')
      .attr('x', d => x(d.step))
      .attr('y', d => y(d.value) - 10)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text(d => d.value);
    
    svg.selectAll('.cognitive-label')
      .data(cognitiveData)
      .enter()
      .append('text')
      .attr('class', 'cognitive-label')
      .attr('x', d => x(d.step))
      .attr('y', d => y(d.value) - 10)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text(d => d.value);
    
    if (currentNestedDepth) {
      svg.selectAll('.depth-label')
        .data(nestedDepthData)
        .enter()
        .append('text')
        .attr('class', 'depth-label')
        .attr('x', d => x(d.step))
        .attr('y', d => y(d.value) - 10)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .text(d => d.value);
    }
    
    const legend = svg.append('g')
      .attr('transform', `translate(${width + 10}, 0)`);
    
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#3b82f6');
    
    legend.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .text('Complexity')
      .style('font-size', '12px');
    
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 25)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#f59e0b');
    
    legend.append('text')
      .attr('x', 20)
      .attr('y', 37)
      .text('Cognitive')
      .style('font-size', '12px');
    
    if (currentNestedDepth) {
      legend.append('rect')
        .attr('x', 0)
        .attr('y', 50)
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', '#10b981');
      
      legend.append('text')
        .attr('x', 20)
        .attr('y', 62)
        .text('Nesting')
        .style('font-size', '12px');
    }
    
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text('Estimated Complexity Reduction with Refactoring');
      
  }, [currentComplexity, currentCognitiveComplexity, currentNestedDepth]);
  
  return (
    <div className={`complexity-timeline ${className}`}>
      <svg ref={svgRef}></svg>
      <div className="mt-4 text-sm text-gray-600">
        <p>This chart illustrates the potential reduction in complexity metrics through incremental refactoring steps.</p>
        <p>Each step assumes approximately 15% complexity reduction from the previous state.</p>
      </div>
    </div>
  );
};

export default ComplexityTimeline;