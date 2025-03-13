import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import * as d3 from 'd3';
import { GraphData, CodeNode, CodeSmell, CodeLink } from '../types';
import { fetchGraphData } from '../services/dataServices';
import { debounce } from 'lodash';

const VisualizationPage: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [width, setWidth] = useState<number>(window.innerWidth);
  const [height, setHeight] = useState<number>(window.innerHeight);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const simulationRef = useRef<d3.Simulation<CodeNode, CodeLink> | null>(null);
  const gRef = useRef<d3.Selection<SVGGElement, unknown, null, undefined> | null>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const nodeDataByIdRef = useRef<Map<string, CodeNode>>(new Map());

  const getNodeSize = useCallback((node: CodeNode) => {
    if (node.type === 'module') return 12;
    if (node.type === 'class') return 10;
    return 8;
  }, []);

  const getNodeFillColor = useCallback((node: CodeNode) => {
    if (node.is_entry) return '#fbbf24';
    if (node.metrics && (
      (node.metrics.complexity && node.metrics.complexity > 10) ||
      (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15) ||
      (node.type === 'class' && node.metrics.complexity && node.metrics.complexity > 50)
    )) return '#ef4444';
    return '#fff';
  }, []);

  const getNodeStrokeColor = useCallback((node: CodeNode) => {
    if (node.type === 'module') return '#0284c7';
    if (node.type === 'class') return '#0891b2';
    return '#0d9488';
  }, []);

  const getCategory = useCallback((smell: string | CodeSmell) => {
    if (typeof smell === 'string') {
      if (smell.startsWith('[')) {
        const endIndex = smell.indexOf(']', 1);
        if (endIndex !== -1) return smell.slice(1, endIndex).toLowerCase();
      }
      return 'unknown';
    } else if (smell.category) {
      return smell.category.toLowerCase();
    }
    return 'unknown';
  }, []);

  const escapeHtml = (text: string) => {
    return text.replace(/[&<>"']/g, (m) => {
      switch (m) {
        case '&': return '&amp;';
        case '<': return '&lt;';
        case '>': return '&gt;';
        case '"': return '&quot;';
        case "'": return '&#39;';
        default: return m;
      }
    });
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const graphData = await fetchGraphData();
        const nodeMap = new Map<string, CodeNode>();
        graphData.nodes.forEach(node => nodeMap.set(node.id, node));
        nodeDataByIdRef.current = nodeMap;
        setData(graphData);
        setError(null);
      } catch (err) {
        console.error('Error loading graph data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setWidth(window.innerWidth);
      setHeight(window.innerHeight);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    svg.selectAll('*').remove();

    const defs = svg.append('defs');
    ['imports', 'contains', 'calls'].forEach(type => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 15)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('fill', type === 'imports' ? '#7c3aed' : type === 'contains' ? '#059669' : '#ea580c')
        .attr('d', 'M0,-5L10,0L0,5');
    });

    const g = svg.append('g');
    gRef.current = g;

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => g.attr('transform', event.transform.toString()));
    zoomRef.current = zoom;
    svg.call(zoom);

    const tooltip = d3.select(containerRef.current)
      .append('div')
      .attr('class', 'absolute p-3 bg-white rounded-lg shadow-md pointer-events-none text-sm max-w-xs opacity-0 z-50')
      .style('z-index', '1000');

    const chargeStrength = Math.min(-400, -30000 / Math.sqrt(data.nodes.length));
    const simulation = d3.forceSimulation<CodeNode, CodeLink>(data.nodes)
      .force('link', d3.forceLink<CodeNode, CodeLink>().id(d => d.id).distance(100).strength(0.5))
      .force('charge', d3.forceManyBody().strength(chargeStrength).distanceMax(500))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(25))
      .force('x', d3.forceX(width / 2).strength(0.05))
      .force('y', d3.forceY(height / 2).strength(0.05))
      .alphaDecay(data.nodes.length > 1000 ? 0.1 : 0.05)
      .velocityDecay(0.4);
    simulationRef.current = simulation;

    const linkSelection = g.append('g')
      .selectAll('path')
      .data(data.links)
      .join('path')
      .attr('class', d => `link link-${d.type}`)
      .attr('marker-end', d => `url(#arrow-${d.type})`)
      .attr('stroke-width', '1.5px')
      .attr('fill', 'none')
      .style('opacity', 0.7)
      .style('stroke', d => {
        if (d.type === 'imports') return '#7c3aed';
        if (d.type === 'contains') return '#059669';
        return '#ea580c';
      });

    const nodeSelection = g.append('g')
      .selectAll('.node')
      .data(data.nodes)
      .join('g')
      .attr('class', d => `node node-${d.type}`)
      .style('cursor', 'pointer');

    const dragBehavior = d3.drag<SVGGElement, CodeNode>()
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
      });
    (nodeSelection as any).call(dragBehavior);

    nodeSelection.append('circle')
      .attr('r', getNodeSize)
      .style('fill', getNodeFillColor)
      .style('stroke', getNodeStrokeColor)
      .style('stroke-width', '2px');

    nodeSelection.append('text')
      .attr('dy', '.35em')
      .attr('x', d => getNodeSize(d) + 8)
      .attr('class', 'node-text')
      .text(d => d.name)
      .style('font', '12px "Segoe UI", sans-serif')
      .style('font-weight', '500')
      .style('text-anchor', 'start')
      .style('fill', '#333');

    nodeSelection
      .on('mouseover', (event, d) => {
        const connections = data.links.filter(l =>
          (typeof l.source === 'string' ? l.source : l.source.id) === d.id ||
          (typeof l.target === 'string' ? l.target : l.target.id) === d.id
        );

        let tooltipContent = `<strong>${escapeHtml(d.name)}</strong> <span style="color: #666;">(${escapeHtml(d.type)})</span><br>`;

        const hasQualityIssues = d.code_smells && d.code_smells.length > 0;
        const hasComplexity = d.metrics && (
          (d.metrics.complexity && d.metrics.complexity > 10) ||
          (d.metrics.cognitive_complexity && d.metrics.cognitive_complexity > 15)
        );
        const hasSqlInjection = d.code_smells && d.code_smells.some(smell => getCategory(smell) === 'sql_injection');
        const hasSecurityIssues = d.code_smells && d.code_smells.some(smell => getCategory(smell) === 'security');
        const hasStyleIssues = d.code_smells && d.code_smells.some(smell => getCategory(smell) === 'style');

        if (hasQualityIssues || hasComplexity || hasSqlInjection || hasSecurityIssues || hasStyleIssues) {
          tooltipContent += '<div style="margin: 5px 0; padding: 5px; background: #fee2e2; border-left: 4px solid #ef4444; border-radius: 3px;">';
          tooltipContent += '<strong style="color: #b91c1c;">⚠️ Issues Detected:</strong><br>';

          if (hasSecurityIssues) {
            const count = d.code_smells?.filter(smell => getCategory(smell) === 'security').length || 0;
            tooltipContent += `• <span style="color: #b91c1c;">${escapeHtml(String(count))} security vulnerability${count === 1 ? '' : 'ies'} detected!</span><br>`;
          }

          if (hasSqlInjection) {
            const count = d.code_smells?.filter(smell => getCategory(smell) === 'sql_injection').length || 0;
            tooltipContent += `• <span style="color: #b91c1c;">${escapeHtml(String(count))} potential SQL injection risk${count === 1 ? '' : 's'}!</span><br>`;
          }

          if (hasComplexity) {
            const complexity = d.metrics?.complexity || 0;
            const cognitiveComplexity = d.metrics?.cognitive_complexity || 0;
            if (complexity > 10) tooltipContent += `• <span style="color: #b91c1c;">High cyclomatic complexity (${complexity})</span><br>`;
            if (cognitiveComplexity > 15) tooltipContent += `• <span style="color: #b91c1c;">High cognitive complexity (${cognitiveComplexity})</span><br>`;
          }

          if (hasStyleIssues) {
            const count = d.code_smells?.filter(smell => getCategory(smell) === 'style').length || 0;
            tooltipContent += `• <span style="color: #0369a1;">${escapeHtml(String(count))} style issue${count === 1 ? '' : 's'}</span><br>`;
          }

          const otherIssues = d.code_smells?.filter(smell =>
            !['security', 'sql_injection', 'style'].includes(getCategory(smell))) || [];
          if (otherIssues.length > 0) {
            tooltipContent += `• <span style="color: #b91c1c;">${escapeHtml(String(otherIssues.length))} other code quality issues</span><br>`;
          }

          tooltipContent += '</div>';
        }

        if (d.docstring) {
          tooltipContent += `<div style="color: #059669; margin: 5px 0;"><em>${escapeHtml(d.docstring)}</em></div>`;
        }

        if (d.type === 'class' && d.methods) {
          tooltipContent += `<br><strong style="color: #0891b2;">Methods:</strong><br>`;
          let methodsShown = 0;
          for (const [methodName] of Object.entries(d.methods)) {
            if (methodsShown < 3) {
              tooltipContent += `• ${escapeHtml(methodName)}<br>`;
              methodsShown++;
            }
          }
          if (Object.keys(d.methods).length > 3) {
            tooltipContent += `<em>...and ${Object.keys(d.methods).length - 3} more</em><br>`;
          }
        }

        if (d.metrics) {
          tooltipContent += '<br><strong style="color: #0891b2;">Metrics Summary:</strong><br>';
          if (d.metrics.lines) tooltipContent += `• Lines: ${escapeHtml(String(d.metrics.lines))}<br>`;
          if (d.metrics.functions) tooltipContent += `• Functions: ${escapeHtml(String(d.metrics.functions))}<br>`;
          if (d.metrics.classes) tooltipContent += `• Classes: ${escapeHtml(String(d.metrics.classes))}<br>`;
        }

        if (connections.length > 0) {
          tooltipContent += `<br><strong style="color: #0891b2;">Connections:</strong> ${connections.length} total<br>`;
          tooltipContent += `<em style="font-size: 0.9em;">Click to view details</em>`;
        }

        tooltip.html(tooltipContent)
          .style('left', `${event.pageX + 10}px`)
          .style('top', `${event.pageY - 10}px`)
          .transition()
          .duration(200)
          .style('opacity', 0.9);

        nodeSelection.style('opacity', n => n.id === d.id || connections.some(c =>
          (typeof c.source === 'string' ? c.source : c.source.id) === n.id ||
          (typeof c.target === 'string' ? c.target : c.target.id) === n.id
        ) ? 1 : 0.1);

        linkSelection.style('opacity', l =>
          (typeof l.source === 'string' ? l.source : l.source.id) === d.id ||
          (typeof l.target === 'string' ? l.target : l.target.id) === d.id ? 1 : 0.1
        );
      })
      .on('mouseout', () => {
        tooltip.transition()
          .duration(500)
          .style('opacity', 0);
        nodeSelection.style('opacity', 1);
        linkSelection.style('opacity', 0.7);
      })
      .on('click', (_, d) => navigate(`/node/${d.id}`));

    const ticked = () => {
      linkSelection.attr('d', d => {
        const source = typeof d.source === 'string' ? data.nodes.find(n => n.id === d.source) || { x: 0, y: 0 } : d.source;
        const target = typeof d.target === 'string' ? data.nodes.find(n => n.id === d.target) || { x: 0, y: 0 } : d.target;
        return `M${source.x},${source.y}L${target.x},${target.y}`;
      });
      nodeSelection.attr('transform', d => `translate(${d.x || 0},${d.y || 0})`);
    };
    simulation.on('tick', ticked);
    simulation.force<d3.ForceLink<CodeNode, CodeLink>>('link')?.links(data.links);

    // **Cleanup**
    return () => {
      tooltip.remove();
      if (simulationRef.current) simulationRef.current.stop();
    };
  }, [data, width, height, navigate]);

  const resetZoom = () => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current)
        .transition()
        .duration(750)
        .call(zoomRef.current.transform, d3.zoomIdentity);
    }
  };

  const debouncedSearch = useCallback(
    debounce((term: string) => {
      if (!svgRef.current) return;
      const svg = d3.select(svgRef.current);
      const nodeSelection = svg.selectAll('.node');
      const linkSelection = svg.selectAll('path');

      if (term === '') {
        nodeSelection.style('opacity', 1);
        linkSelection.style('opacity', 0.7);
        return;
      }

      const lowerTerm = term.toLowerCase();
      const matchedNodes = new Set<string>();

      data.nodes.forEach(node => {
        if (node.name.toLowerCase().includes(lowerTerm)) {
          matchedNodes.add(node.id);
          data.links.forEach(l => {
            const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
            const targetId = typeof l.target === 'string' ? l.target : l.target.id;
            if (sourceId === node.id) matchedNodes.add(targetId);
            if (targetId === node.id) matchedNodes.add(sourceId);
          });
        }
      });

      nodeSelection.style('opacity', (d: unknown) => matchedNodes.has((d as CodeNode).id) ? 1 : 0.1);
      linkSelection.style('opacity', (d: unknown) => {
        const l = d as CodeLink;
        const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
        const targetId = typeof l.target === 'string' ? l.target : l.target.id;
        return matchedNodes.has(sourceId) && matchedNodes.has(targetId) ? 0.7 : 0.1;
      });
    }, 200),
    [data]
  );

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    debouncedSearch(term);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading visualization data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen flex-col">
        <div className="text-xl text-red-600 mb-4">Error loading data</div>
        <div className="text-gray-700">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative w-full h-screen overflow-hidden bg-gray-50">
      <div className="fixed top-5 left-5 bg-white p-4 rounded-xl shadow-md z-10 flex flex-wrap gap-4 items-center">
        <div>
          <input
            type="text"
            id="search"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="w-64 p-2 border border-gray-200 rounded-md text-sm"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={resetZoom}
            className="bg-blue-700 text-white border-none px-4 py-2 rounded-md cursor-pointer text-sm transition-colors hover:bg-blue-800"
          >
            Reset View
          </button>
        </div>
      </div>

      <div className="fixed bottom-5 left-5 bg-white p-4 rounded-xl shadow-md z-10">
        <h3 className="mt-0 mb-3 text-base text-gray-900">Legend</h3>
        <div className="flex items-center mb-2 text-sm">
          <div className="w-4 h-4 rounded bg-blue-600 mr-2"></div>
          <span>Module</span>
        </div>
        <div className="flex items-center mb-2 text-sm">
          <div className="w-4 h-4 rounded bg-amber-400 mr-2"></div>
          <span>Entry Point</span>
        </div>
        <div className="flex items-center mb-2 text-sm">
          <div className="w-4 h-4 rounded bg-cyan-600 mr-2"></div>
          <span>Class</span>
        </div>
        <div className="flex items-center mb-2 text-sm">
          <div className="w-4 h-4 rounded bg-teal-600 mr-2"></div>
          <span>Function</span>
        </div>
        <div className="mt-4 border-t border-gray-200 pt-3">
          <div className="flex items-center mb-2 text-sm">
            <div className="w-10 h-0.5 bg-purple-600 mr-2"></div>
            <span>Imports</span>
          </div>
          <div className="flex items-center mb-2 text-sm">
            <div className="w-10 h-0.5 bg-green-600 mr-2"></div>
            <span>Contains</span>
          </div>
          <div className="flex items-center mb-2 text-sm">
            <div className="w-10 h-0.5 bg-orange-600 mr-2"></div>
            <span>Calls</span>
          </div>
        </div>
      </div>

      <svg ref={svgRef} id="visualization" className="w-full h-screen"></svg>
      <div className="fixed top-5 right-5 z-10">
        <button
          onClick={() => navigate('/project-metrics')}
          className="bg-white text-indigo-700 border border-indigo-300 px-4 py-2 rounded-lg shadow-md hover:bg-indigo-50 transition-colors duration-200 flex items-center gap-2 font-medium"
          aria-label="View Project Metrics"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zm6-4a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zm6-3a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
          </svg>
          View Project Metrics
        </button>
      </div>
    </div>
  );
};

export default VisualizationPage;