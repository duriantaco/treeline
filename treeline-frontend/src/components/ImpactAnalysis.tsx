import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ImpactAnalysisProps {
  nodeId: string;
  nodeName: string;
  nodeType: string;
  connections: {
    incoming: Array<any>;
    outgoing: Array<any>;
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
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    d3.select(svgRef.current).selectAll('*').remove();

    const width = 600;
    const height = 400;
    const tooltip = tooltipRef.current;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const tooltipDiv = tooltip ? d3.select(tooltip) : d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0)
      .style("position", "absolute")
      .style("background-color", "white")
      .style("border", "1px solid #ccc")
      .style("border-radius", "5px")
      .style("padding", "10px")
      .style("pointer-events", "none");

    const allNodes: any[] = [];
    const allLinks: any[] = [];
    const riskScores: {[key: string]: number} = {};
    const impactScores: {[key: string]: number} = {};

    allNodes.push({
      id: nodeId,
      name: nodeName,
      type: nodeType,
      level: 0,
      isCenter: true,
      hasIssues,
      highComplexity,
      x: width / 2,
      y: height / 2,
    });

    const addedNodeIds = new Set([nodeId]);

    const extractNodeData = (conn: any, isSource: boolean, fallbackId: string): any => {
      if (typeof conn === 'string') {
        return { id: conn, name: conn, type: 'unknown' };
      }
      
      if (!conn || typeof conn !== 'object') {
        return { id: fallbackId, name: fallbackId, type: 'unknown' };
      }
      
      if (isSource) {
        return {
          id: conn.source_id || conn.source || conn.id || fallbackId,
          name: conn.source_name || (conn.source && typeof conn.source === 'object' ? conn.source.name : conn.source) || conn.name || fallbackId,
          type: conn.source_type || (conn.source && typeof conn.source === 'object' ? conn.source.type : '') || conn.type || 'unknown',
          metrics: conn.metrics || (conn.source && typeof conn.source === 'object' ? conn.source.metrics : {}) || {},
          issues: conn.code_smells?.length || (conn.source && typeof conn.source === 'object' ? conn.source.code_smells?.length : 0) || 0
        };
      } else {
        return {
          id: conn.target_id || conn.target || conn.id || fallbackId,
          name: conn.target_name || (conn.target && typeof conn.target === 'object' ? conn.target.name : conn.target) || conn.name || fallbackId,
          type: conn.target_type || (conn.target && typeof conn.target === 'object' ? conn.target.type : '') || conn.type || 'unknown',
          metrics: conn.metrics || (conn.target && typeof conn.target === 'object' ? conn.target.metrics : {}) || {},
          issues: conn.code_smells?.length || (conn.target && typeof conn.target === 'object' ? conn.target.code_smells?.length : 0) || 0
        };
      }
    };

    if (connections.incoming && Array.isArray(connections.incoming)) {
      connections.incoming.forEach((conn, index) => {
        const sourceData = extractNodeData(conn, true, `incoming-${index}`);
        const sourceId = sourceData.id;
        
        if (!sourceId) return;
        
        const sourceName = sourceData.name;
        const sourceType = sourceData.type;
        const sourceIssues = sourceData.issues || 0;
        
        riskScores[sourceId] = Math.min(10, sourceIssues + (sourceType === 'module' ? 3 : sourceType === 'class' ? 2 : 1));

        if (!addedNodeIds.has(sourceId)) {
          const angle = (2 * Math.PI / (connections.incoming.length)) * index;
          const radius = 150;
          const x = width / 2 - radius * Math.cos(angle);
          const y = height / 2 - radius * Math.sin(angle);

          allNodes.push({
            id: sourceId,
            name: sourceName,
            type: sourceType,
            level: 1,
            direction: 'incoming',
            x,
            y,
            issues: sourceIssues,
            metrics: sourceData.metrics
          });
          addedNodeIds.add(sourceId);
        }

        const linkType = conn.type || 'unknown';
        
        let impactWeight = 1;
        if (linkType === 'imports') impactWeight = 3;
        else if (linkType === 'contains') impactWeight = 2;
        else if (linkType === 'calls') impactWeight = 1;
        
        impactScores[sourceId] = (impactScores[sourceId] || 0) + impactWeight;

        allLinks.push({
          source: sourceId,
          target: nodeId,
          type: linkType,
          direction: 'incoming',
        });
      });
    }

    if (connections.outgoing && Array.isArray(connections.outgoing)) {
      connections.outgoing.forEach((conn, index) => {
        const targetData = extractNodeData(conn, false, `outgoing-${index}`);
        const targetId = targetData.id;
        
        if (!targetId) return;
        
        const targetName = targetData.name;
        const targetType = targetData.type;
        const targetIssues = targetData.issues || 0;
        
        riskScores[targetId] = Math.min(10, targetIssues + (targetType === 'module' ? 3 : targetType === 'class' ? 2 : 1));

        if (!addedNodeIds.has(targetId)) {
          const angle = (2 * Math.PI / (connections.outgoing.length)) * index + Math.PI; // Offset angle
          const radius = 150;
          const x = width / 2 + radius * Math.cos(angle);
          const y = height / 2 + radius * Math.sin(angle);

          allNodes.push({
            id: targetId,
            name: targetName,
            type: targetType,
            level: 1,
            direction: 'outgoing',
            x,
            y,
            issues: targetIssues,
            metrics: targetData.metrics
          });
          addedNodeIds.add(targetId);
        }

        const linkType = conn.type || 'unknown';
        
        let impactWeight = 1;
        if (linkType === 'imports') impactWeight = 3;
        else if (linkType === 'contains') impactWeight = 2;
        else if (linkType === 'calls') impactWeight = 1;
        
        impactScores[targetId] = (impactScores[targetId] || 0) + impactWeight;

        allLinks.push({
          source: nodeId,
          target: targetId,
          type: linkType,
          direction: 'outgoing',
        });
      });
    }

    riskScores[nodeId] = Math.min(10, (highComplexity ? 5 : 0) + (hasIssues ? 5 : 0));
    impactScores[nodeId] = 10;
    
    console.log('Nodes to render:', allNodes.length, allNodes);
    console.log('Links to render:', allLinks.length, allLinks);

    const simulation = d3.forceSimulation(allNodes)
      .force('link', d3.forceLink(allLinks).id((d: any) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-1000)) 
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40)) 
      .force('x', d3.forceX(width / 2).strength(0.1))
      .force('y', d3.forceY(height / 2).strength(0.1));

    const link = svg.append('g')
      .selectAll('path')
      .data(allLinks)
      .enter()
      .append('path')
      .attr('stroke', d => {
        if (d.type === 'imports') return '#7c3aed';
        if (d.type === 'contains') return '#059669';
        if (d.type === 'calls') return '#ea580c';
        return '#888888';
      })
      .attr('stroke-width', 2)
      .attr('marker-end', d => `url(#impact-arrow-${d.type})`)
      .attr('fill', 'none');

    const node = svg.append('g')
      .selectAll('.node')
      .data(allNodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .call(d3.drag<any, any>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    node.append('circle')
      .attr('r', d => (d.isCenter ? 15 : 10))
      .attr('fill', d => {
        if (d.isCenter) {
          return highComplexity ? '#ef4444' : hasIssues ? '#f59e0b' : '#3b82f6';
        } else {
          const riskScore = riskScores[d.id] || 0;
          return riskScore > 7 ? '#ef4444' : 
                 riskScore > 4 ? '#f59e0b' :
                 riskScore > 0 ? '#3b82f6' : '#d1d5db';
        }
      });

    node.append('circle')
      .attr('r', d => ((impactScores[d.id] || 0) * 2) + 10)
      .attr('fill', 'none')
      .attr('stroke', d => {
        const impactScore = impactScores[d.id] || 0;
        return impactScore > 7 ? '#ef4444' : 
               impactScore > 4 ? '#f59e0b' : '#10b981';
      })
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '3,3');

    node.append('text')
      .attr('dx', 15)
      .attr('dy', 5)
      .text(d => d.name)
      .style('font-size', '12px')
      .style('font-family', 'sans-serif');

    node.on('mouseover', function(event, d) {
      tooltipDiv.transition()
        .duration(200)
        .style('opacity', 0.9);
      
      let tooltipContent = `<strong>${d.name}</strong> (${d.type})<br/>`;
      tooltipContent += `Risk Score: ${riskScores[d.id] || 0}/10<br/>`;
      tooltipContent += `Impact Score: ${impactScores[d.id] || 0}/10<br/>`;
      
      if (d.issues > 0) {
        tooltipContent += `Issues: ${d.issues}<br/>`;
      }
      
      if (d.metrics) {
        if (d.metrics.complexity) tooltipContent += `Complexity: ${d.metrics.complexity}<br/>`;
        if (d.metrics.lines) tooltipContent += `Lines: ${d.metrics.lines}<br/>`;
        if (d.metrics.functions) tooltipContent += `Functions: ${d.metrics.functions}<br/>`;
        if (d.metrics.classes) tooltipContent += `Classes: ${d.metrics.classes}<br/>`;
      }
      
      tooltipDiv.html(tooltipContent)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    })
    .on('mouseout', function() {
      tooltipDiv.transition()
        .duration(500)
        .style('opacity', 0);
    });

    simulation.on('tick', () => {
      link.attr('d', d => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    const defs = svg.append('defs');
    ['imports', 'contains', 'calls', 'unknown'].forEach(type => {
      defs.append('marker')
        .attr('id', `impact-arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('fill', type === 'imports' ? '#7c3aed' : type === 'contains' ? '#059669' : type === 'calls' ? '#ea580c' : '#888888')
        .attr('d', 'M0,-5L10,0L0,5');
    });

    const legend = svg.append('g')
      .attr('transform', `translate(${width - 160}, 20)`);
    
    legend.append('rect')
      .attr('width', 150)
      .attr('height', 140)
      .attr('fill', 'white')
      .attr('stroke', '#ccc')
      .attr('rx', 5)
      .attr('ry', 5);
    
    legend.append('text')
      .attr('x', 10)
      .attr('y', 20)
      .text('Impact Legend')
      .style('font-weight', 'bold')
      .style('font-size', '12px');
    
    const legendItems = [
      { color: '#ef4444', text: 'High Impact/Risk' },
      { color: '#f59e0b', text: 'Medium Impact/Risk' },
      { color: '#10b981', text: 'Low Impact/Risk' },
      { color: '#7c3aed', text: 'Imports Relation' },
      { color: '#059669', text: 'Contains Relation' },
      { color: '#ea580c', text: 'Calls Relation' }
    ];
    
    legendItems.forEach((item, i) => {
      const y = 35 + i * 18;
      
      if (i === 3) {
        legend.append('line')
          .attr('x1', 10)
          .attr('y1', y - 9)
          .attr('x2', 140)
          .attr('y2', y - 9)
          .attr('stroke', '#ccc')
          .attr('stroke-dasharray', '2,2');
      }
      
      legend.append('rect')
        .attr('x', 10)
        .attr('y', y - 6)
        .attr('width', 12)
        .attr('height', 12)
        .attr('fill', item.color);
        
      legend.append('text')
        .attr('x', 28)
        .attr('y', y)
        .text(item.text)
        .style('font-size', '10px');
    });

    svg.append('text')
      .attr('x', 10)
      .attr('y', height - 10)
      .text(`Connections: ${allLinks.length} | Impact Radius: ${impactScores[nodeId] || 0}/10`)
      .style('font-size', '12px')
      .style('fill', '#666');

  }, [nodeId, nodeName, nodeType, connections, hasIssues, highComplexity]);

  return (
    <div className="impact-analysis">
      <div ref={tooltipRef} className="tooltip" style={{ opacity: 0 }}></div>
      <svg ref={svgRef}></svg>
      <div className="mt-4 text-sm text-gray-600">
        <p>This visualization shows the potential impact of changes to this component. Larger circles indicate higher impact radius.</p>
        <p>Red nodes indicate high risk components. You can drag nodes to rearrange the visualization.</p>
      </div>
    </div>
  );
};

export default ImpactAnalysis;