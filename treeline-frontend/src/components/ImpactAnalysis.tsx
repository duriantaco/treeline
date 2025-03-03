import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { CodeLink } from '../types';

interface ImpactAnalysisProps {
  nodeId: string;
  nodeName: string;
  nodeType: string;
  connections: {
    incoming: CodeLink[];
    outgoing: CodeLink[];
  };
  hasIssues: boolean;
  highComplexity: boolean;
}

const ImpactAnalysis: React.FC<ImpactAnalysisProps> = ({
  nodeId,
  nodeName,
  nodeType,
  connections,
  hasIssues,
  highComplexity,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    d3.select(svgRef.current).selectAll('*').remove();

    const width = 600;
    const height = 400;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const nodes: any[] = [];
    const links: any[] = [];
    
    const addedNodes = new Set<string>([nodeId]);
    const secondaryNodes = new Set<string>();
    
    nodes.push({
      id: nodeId,
      name: nodeName,
      type: nodeType,
      level: 0,
      isCenter: true,
      hasIssues,
      highComplexity
    });
    connections.incoming.forEach(connection => {
      const sourceId = typeof connection.source === 'object' ? connection.source.id : connection.source;
      const sourceName = typeof connection.source === 'object' ? connection.source.name : `Node ${sourceId}`;
      const sourceType = typeof connection.source === 'object' ? connection.source.type : 'unknown';
      
      if (!addedNodes.has(sourceId)) {
        nodes.push({
          id: sourceId,
          name: sourceName,
          type: sourceType,
          level: 1,
          direction: 'incoming'
        });
        addedNodes.add(sourceId);
        secondaryNodes.add(sourceId);
      }
      
      links.push({
        source: sourceId,
        target: nodeId,
        type: connection.type,
        direction: 'incoming'
      });
    });
    
    connections.outgoing.forEach(connection => {
      const targetId = typeof connection.target === 'object' ? connection.target.id : connection.target;
      const targetName = typeof connection.target === 'object' ? connection.target.name : `Node ${targetId}`;
      const targetType = typeof connection.target === 'object' ? connection.target.type : 'unknown';
      
      if (!addedNodes.has(targetId)) {
        nodes.push({
          id: targetId,
          name: targetName,
          type: targetType,
          level: 1,
          direction: 'outgoing'
        });
        addedNodes.add(targetId);
        secondaryNodes.add(targetId);
      }
      
      links.push({
        source: nodeId,
        target: targetId,
        type: connection.type,
        direction: 'outgoing'
      });
    });
    

    const impactScores = new Map<string, number>();
    
    impactScores.set(nodeId, 10);
    
    nodes.forEach(node => {
      if (node.id === nodeId) return;
      
      let score = 5;
      
      const directConnections = links.filter(link => 
        link.source === node.id || link.target === node.id
      );
      
      directConnections.forEach(link => {
        if (link.type === 'contains') score += 3;
        else if (link.type === 'imports') score += 2;
        else if (link.type === 'calls') score += 1;
      });
      
      if (node.type === 'module') score += 3;
      else if (node.type === 'class') score += 2;
      else if (node.type === 'function') score += 1;
      
      score = Math.min(10, Math.max(0, score));
      
      impactScores.set(node.id, score);
    });
    
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));
    
    const defs = svg.append('defs');
    ['imports', 'contains', 'calls'].forEach(type => {
      defs.append('marker')
        .attr('id', `impact-arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('fill', type === 'imports' ? '#7c3aed' : type === 'contains' ? '#059669' : '#ea580c')
        .attr('d', 'M0,-5L10,0L0,5');
    });
    
    const link = svg.append('g')
      .selectAll('path')
      .data(links)
      .enter()
      .append('path')
      .attr('stroke', d => {
        if (d.type === 'imports') return '#7c3aed';
        if (d.type === 'contains') return '#059669';
        return '#ea580c';
      })
      .attr('stroke-width', d => {
        if (d.source === nodeId || d.target === nodeId) return 2;
        return 1.5;
      })
      .attr('stroke-opacity', d => {
        if (d.source === nodeId || d.target === nodeId) return 0.8;
        return 0.6;
      })
      .attr('marker-end', d => `url(#impact-arrow-${d.type})`)
      .attr('fill', 'none');
    
    const node = svg.append('g')
      .selectAll('.node')
      .data(nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));
    
    node.append('circle')
      .attr('r', d => {
        if (d.isCenter) return 15;
        return 10;
      })
      .attr('fill', d => {
        if (d.isCenter) return highComplexity ? '#ef4444' : (hasIssues ? '#f59e0b' : '#3b82f6');
        if (d.type === 'module') return '#93c5fd';
        if (d.type === 'class') return '#67e8f9';
        if (d.type === 'function') return '#6ee7b7';
        return '#d1d5db';
      })
      .attr('stroke', d => {
        if (d.isCenter) return '#3b82f6';
        if (d.type === 'module') return '#1d4ed8';
        if (d.type === 'class') return '#0e7490';
        if (d.type === 'function') return '#047857';
        return '#6b7280';
      })
      .attr('stroke-width', d => d.isCenter ? 3 : 1.5);
    
    node.append('circle')
      .attr('r', d => {
        const score = impactScores.get(d.id) || 0;
        return score * 2; 
      })
      .attr('fill', 'none')
      .attr('stroke', d => {
        const score = impactScores.get(d.id) || 0;
        if (score >= 7) return '#ef4444';
        if (score >= 4) return '#f59e0b';
        return '#10b981';
      })
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '3,3')
      .attr('stroke-opacity', 0.7);
    
    node.append('text')
      .attr('dx', 15)
      .attr('dy', 5)
      .text(d => d.name)
      .attr('font-size', d => d.isCenter ? '14px' : '12px')
      .attr('font-weight', d => d.isCenter ? 'bold' : 'normal');
    
    node.select('text')
      .each(function() {
        const textElement = this as SVGTextElement;
        const bbox = textElement.getBBox();
        
        const parent = textElement.parentNode as SVGGElement;
        d3.select(parent)
          .insert('rect', 'text')
          .attr('x', bbox.x - 2)
          .attr('y', bbox.y - 2)
          .attr('width', bbox.width + 4)
          .attr('height', bbox.height + 4)
          .attr('fill', 'white')
          .attr('fill-opacity', 0.8)
          .attr('rx', 3);
      });
    
    node.append('title')
      .text(d => {
        const score = impactScores.get(d.id) || 0;
        return `${d.name} (${d.type})\nImpact Score: ${score.toFixed(1)}/10`;
      });
    
    simulation.on('tick', () => {
      link.attr('d', d => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy);
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });
      
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    const legend = svg.append('g')
      .attr('transform', `translate(10, 20)`);
    
    legend.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .text('Impact Analysis')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold');
    
    const legendItems = [
      { color: '#3b82f6', label: 'Current Node' },
      { color: '#ef4444', label: 'High Impact' },
      { color: '#f59e0b', label: 'Medium Impact' },
      { color: '#10b981', label: 'Low Impact' }
    ];
    
    legendItems.forEach((item, i) => {
      legend.append('rect')
        .attr('x', 0)
        .attr('y', 25 + i * 20)
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', item.color);
      
      legend.append('text')
        .attr('x', 25)
        .attr('y', 25 + i * 20 + 12)
        .text(item.label)
        .attr('font-size', '12px');
    });
    
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }, [nodeId, nodeName, nodeType, connections, hasIssues, highComplexity]);

  return (
    <div className="impact-analysis">
      <svg ref={svgRef}></svg>
      <div className="mt-4 text-sm text-gray-600">
        <p>This visualization shows the potential impact of changes to this component on other parts of the codebase.</p>
        <p>Larger dotted circles indicate higher potential impact. Nodes can be dragged to rearrange the visualization.</p>
      </div>
    </div>
  );
};

export default ImpactAnalysis;