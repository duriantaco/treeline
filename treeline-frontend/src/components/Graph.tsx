import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface GraphProps {
  data: { nodes: any[]; links: any[] };
  onNodeClick: (node: any) => void;
}

const Graph: React.FC<GraphProps> = ({ data, onNodeClick }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current).attr('width', 800).attr('height', 600);
    svg.selectAll('*').remove();

    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id((d: any) => d.id))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(400, 300));

    const links = svg.append('g').selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', '#999');

    const nodes = svg.append('g').selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', 5)
      .attr('fill', 'blue')
      .on('click', (_event, d) => onNodeClick(d));

    simulation.on('tick', () => {
      links.attr('x1', (d: any) => d.source.x).attr('y1', (d: any) => d.source.y)
           .attr('x2', (d: any) => d.target.x).attr('y2', (d: any) => d.target.y);
      nodes.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
    });
  }, [data, onNodeClick]);

  return <svg ref={svgRef} />;
};

export default Graph;