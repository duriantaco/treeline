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

  useEffect(() => {
    if (!svgRef.current) return;

    d3.select(svgRef.current).selectAll('*').remove();

    const width = 600;
    const height = 400;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const allNodes: any[] = [];
    const allLinks: any[] = [];

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

    const extractNodeData = (node: any, fallbackId: string) => {
      if (typeof node === 'string') {
        return { id: node, name: node, type: 'unknown' };
      } else if (node && typeof node === 'object') {
        return {
          id: node.id || node.source_id || node.target_id || fallbackId,
          name: node.name || node.source_name || node.target_name || (node.id || fallbackId),
          type: node.type || node.source_type || node.target_type || 'unknown',
        };
      }
      return { id: '', name: '', type: 'unknown' };
    };

    ////// INCOMING /////// 
    if (connections.incoming && Array.isArray(connections.incoming)) {
      const validIncoming = connections.incoming.filter(conn => {
        const sourceData = extractNodeData(conn.source || conn, '');
        const targetData = extractNodeData(conn.target || conn, '');
        if (!sourceData.id || !targetData.id) {
          return false;
        }
        return true;
      });

      validIncoming.forEach((conn, index) => {
        const sourceData = extractNodeData(conn.source || conn, '');
        const sourceId = sourceData.id;
        const sourceName = sourceData.name;
        const sourceType = sourceData.type;

        if (!addedNodeIds.has(sourceId)) {
          const angle = (Math.PI / (validIncoming.length + 1)) * (index + 1);
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
          });
          addedNodeIds.add(sourceId);
        }

        allLinks.push({
          source: sourceId,
          target: nodeId,
          type: conn.type || 'unknown',
          direction: 'incoming',
        });
      });
    }

    /////// OUTGOING ///////
    if (connections.outgoing && Array.isArray(connections.outgoing)) {
      const validOutgoing = connections.outgoing.filter(conn => {
        const sourceData = extractNodeData(conn.source || conn, '');
        const targetData = extractNodeData(conn.target || conn, '');
        if (!sourceData.id || !targetData.id) {
          return false;
        }
        return true;
      });

      validOutgoing.forEach((conn, index) => {
        const targetData = extractNodeData(conn.target || conn, '');
        const targetId = targetData.id;
        const targetName = targetData.name;
        const targetType = targetData.type;

        if (!addedNodeIds.has(targetId)) {
          const angle = (Math.PI / (validOutgoing.length + 1)) * (index + 1);
          const radius = 150;
          const x = width / 2 + radius * Math.cos(angle);
          const y = height / 2 - radius * Math.sin(angle);

          allNodes.push({
            id: targetId,
            name: targetName,
            type: targetType,
            level: 1,
            direction: 'outgoing',
            x,
            y,
          });
          addedNodeIds.add(targetId);
        }

        allLinks.push({
          source: nodeId,
          target: targetId,
          type: conn.type || 'unknown',
          direction: 'outgoing',
        });
      });
    }

    const impactScores = new Map<string, number>();
    impactScores.set(nodeId, 10);

    allNodes.forEach(node => {
      if (node.id === nodeId) return;
      let score = 5;
      const directConnections = allLinks.filter(link =>
        String(link.source) === String(node.id) || String(link.target) === String(node.id)
      );
      directConnections.forEach(link => {
        if (link.type === 'contains') score += 3;
        else if (link.type === 'imports') score += 2;
        else if (link.type === 'calls') score += 1;
      });
      if (node.type === 'module') score += 3;
      else if (node.type === 'class') score += 2;
      else if (node.type === 'function' || node.type === 'method') score += 1;
      score = Math.min(10, Math.max(0, score));
      impactScores.set(node.id, score);
    });

    const simulation = d3.forceSimulation(allNodes)
      .force('link', d3.forceLink(allLinks).id((d: any) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-600))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

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
      .attr('fill', d => (d.isCenter ? (highComplexity ? '#ef4444' : hasIssues ? '#f59e0b' : '#3b82f6') : '#d1d5db'));

    node.append('circle')
      .attr('r', d => (impactScores.get(d.id) || 0) * 2)
      .attr('fill', 'none')
      .attr('stroke', d => {
        const score = impactScores.get(d.id) || 0;
        return score >= 7 ? '#ef4444' : score >= 4 ? '#f59e0b' : '#10b981';
      })
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '3,3');

    node.append('text')
      .attr('dx', 15)
      .attr('dy', 5)
      .text(d => d.name);

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
        .attr('fill', type === 'imports' ? '#7c3aed' : type === 'contains' ? '#059669' : '#ea580c')
        .attr('d', 'M0,-5L10,0L0,5');
    });

    svg.append('text')
      .attr('x', 10)
      .attr('y', 380)
      .text(`Total nodes: ${allNodes.length}, Total links: ${allLinks.length}`);
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