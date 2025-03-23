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
  const [showLegend, setShowLegend] = useState<boolean>(true);
  const navigate = useNavigate();

  const simulationRef = useRef<d3.Simulation<CodeNode, CodeLink> | null>(null);
  const gRef = useRef<d3.Selection<SVGGElement, unknown, null, undefined> | null>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const nodeDataByIdRef = useRef<Map<string, CodeNode>>(new Map());

  const colors = {
    background: '#f8fafc',
    module: '#3b82f6',     // Bright blue
    class: '#06b6d4',      // Cyan
    function: '#0d9488',   // Teal
    entryPoint: '#f59e0b', // Amber
    imports: '#8b5cf6',    // Purple
    contains: '#10b981',   // Emerald
    calls: '#f97316',      // Orange
    error: '#ef4444',      // Red
    security: '#b91c1c',   // Dark red
    tooltip: {
      bg: '#ffffff',
      border: '#e2e8f0',
      shadow: 'rgba(0, 0, 0, 0.1)'
    },
    ui: {
      primary: '#4f46e5',  // Indigo
      secondary: '#64748b', // Slate
      hover: '#4338ca'     // Darker indigo
    }
  };

  const getNodeSize = useCallback((node: CodeNode) => {
    if (node.type === 'module') return 14;
    if (node.type === 'class') return 12;
    return 9;
  }, []);

  const getNodeFillColor = useCallback((node: CodeNode) => {
    if (node.is_entry) return colors.entryPoint;
    
    if (node.metrics && (
      (node.metrics.complexity && node.metrics.complexity > 10) ||
      (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15) ||
      (node.type === 'class' && node.metrics.complexity && node.metrics.complexity > 50)
    )) return '#fca5a5'; 
    
    return '#ffffff'; 
  }, []);

  const getNodeStrokeColor = useCallback((node: CodeNode) => {
    if (node.type === 'module') return colors.module;
    if (node.type === 'class') return colors.class;
    return colors.function;
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
    const handleResize = debounce(() => {
      setWidth(window.innerWidth);
      setHeight(window.innerHeight);
    }, 200);
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;
  
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('class', 'overflow-visible');
  
    svg.selectAll('*').remove();
  
    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
      .attr('id', 'bg-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '100%');
    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#f8fafc');
    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#f1f5f9');
    svg.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'url(#bg-gradient)');
  
    ['imports', 'contains', 'calls'].forEach(type => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 18)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('fill', type === 'imports' ? colors.imports : type === 'contains' ? colors.contains : colors.calls)
        .attr('d', 'M0,-4L8,0L0,4L2,0Z');
    });
  
    const gridSize = 40;
    const gridPattern = defs.append('pattern')
      .attr('id', 'grid')
      .attr('width', gridSize)
      .attr('height', gridSize)
      .attr('patternUnits', 'userSpaceOnUse');
    gridPattern.append('path')
      .attr('d', `M ${gridSize} 0 L 0 0 0 ${gridSize}`)
      .attr('fill', 'none')
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', '0.5');
    svg.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'url(#grid)');
  
    const g = svg.append('g');
    gRef.current = g;
  
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => g.attr('transform', event.transform.toString()));
    zoomRef.current = zoom;
    svg.call(zoom);
  
    const tooltip = d3.select(containerRef.current)
      .append('div')
      .attr('class', 'absolute p-4 bg-white bg-opacity-95 rounded-lg shadow-lg pointer-events-none text-sm max-w-sm opacity-0 z-50 backdrop-blur-sm border border-gray-100')
      .style('transition', 'opacity 0.2s ease-in-out, transform 0.2s ease-in-out')
      .style('transform', 'translateY(10px)')
      .style('z-index', '1000');
  
    const chargeStrength = Math.min(-400, -25000 / Math.sqrt(data.nodes.length));
    const simulation = d3.forceSimulation<CodeNode, CodeLink>(data.nodes)
      .force('link', d3.forceLink<CodeNode, CodeLink>().id(d => d.id).distance(120).strength(0.4))
      .force('charge', d3.forceManyBody().strength(chargeStrength).distanceMax(600))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30))
      .force('x', d3.forceX(width / 2).strength(0.04))
      .force('y', d3.forceY(height / 2).strength(0.04))
      .alphaDecay(0.1) 
      .alphaMin(0.01)
      .alphaDecay(data.nodes.length > 1000 ? 0.1 : 0.05)
      .velocityDecay(0.4);
    simulationRef.current = simulation;
  
    const connectionsMap = new Map<string, Set<string>>();
    data.nodes.forEach(node => {
      connectionsMap.set(node.id, new Set());
    });
    data.links.forEach(link => {
      const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
      const targetId = typeof link.target === 'string' ? link.target : link.target.id;
      connectionsMap.get(sourceId)?.add(targetId);
      connectionsMap.get(targetId)?.add(sourceId);
    });
  
    const linkSelection = g.append('g')
      .selectAll('path')
      .data(data.links)
      .join('path')
      .attr('class', d => `link link-${d.type}`)
      .attr('marker-end', d => `url(#arrow-${d.type})`)
      .attr('stroke-width', '1.5px')
      .attr('fill', 'none')
      .style('opacity', 0)
      .style('stroke', d => {
        if (d.type === 'imports') return colors.imports;
        if (d.type === 'contains') return colors.contains;
        return colors.calls;
      })
      .style('stroke-dasharray', d => d.type === 'imports' ? '4,2' : 'none');
  
    const nodeSelection = g.append('g')
      .selectAll('.node')
      .data(data.nodes)
      .join('g')
      .attr('class', d => `node node-${d.type}`)
      .style('cursor', 'pointer')
      .attr('opacity', 0);
  
    const dragBehavior = d3.drag<SVGGElement, CodeNode>()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
        d3.select(event.sourceEvent.currentTarget)
          .select('circle')
          .attr('r', getNodeSize(d) * 1.2);
      })
      .on('drag', (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
        d3.select(event.sourceEvent.currentTarget)
          .select('circle')
          .attr('r', getNodeSize(d));
      });
    (nodeSelection as any).call(dragBehavior);
  
    nodeSelection.append('circle')
      .attr('r', getNodeSize)
      .attr('fill', getNodeFillColor)
      .attr('stroke', getNodeStrokeColor)
      .attr('stroke-width', '2px')
      .attr('filter', 'url(#drop-shadow)')
      .attr('class', 'transition-all duration-300');
  
    nodeSelection.append('text')
      .attr('dy', '.35em')
      .attr('x', d => getNodeSize(d) + 8)
      .attr('class', 'node-text transition-all duration-300')
      .text(d => d.name)
      .style('font-family', '"Inter", "Segoe UI", system-ui, sans-serif')
      .style('font-size', '12px')
      .style('font-weight', '500')
      .style('text-anchor', 'start')
      .style('fill', '#334155')
      .style('pointer-events', 'none');
  
    setTimeout(() => {
      nodeSelection
        .transition()
        .duration(800)
        .attr('opacity', 1);
      linkSelection
        .transition()
        .duration(800)
        .style('opacity', 0.7);
    }, 100);
  
    data.nodes.forEach(node => {
      let tooltipContent = `
        <div class="flex flex-col gap-2">
          <div class="flex items-start">
            <div class="w-3 h-3 rounded-full mt-1 mr-2" style="background-color: ${getNodeStrokeColor(node)}"></div>
            <div>
              <div class="font-semibold text-gray-800">${escapeHtml(node.name)}</div>
              <div class="text-xs text-gray-500 capitalize">${escapeHtml(node.type)}</div>
            </div>
          </div>
      `;
    
      const hasQualityIssues = node.code_smells && node.code_smells.length > 0;
      const hasComplexity = node.metrics && (
        (node.metrics.complexity && node.metrics.complexity > 10) ||
        (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15)
      );
      const hasSqlInjection = node.code_smells && node.code_smells.some(smell => getCategory(smell) === 'sql_injection');
      const hasSecurityIssues = node.code_smells && node.code_smells.some(smell => getCategory(smell) === 'security');
      const hasStyleIssues = node.code_smells && node.code_smells.some(smell => getCategory(smell) === 'style');
    
      if (hasQualityIssues || hasComplexity || hasSqlInjection || hasSecurityIssues || hasStyleIssues) {
        tooltipContent += `
          <div class="mt-2 p-3 bg-red-50 border-l-4 border-red-500 rounded-md">
            <div class="font-semibold text-red-800 mb-1 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              Issues Detected
            </div>
            <ul class="text-xs space-y-1 text-gray-800">
        `;
        if (hasSecurityIssues) {
          const count = node.code_smells?.filter(smell => getCategory(smell) === 'security').length || 0;
          tooltipContent += `<li class="text-red-800 font-medium">• ${escapeHtml(String(count))} security vulnerability${count === 1 ? '' : 'ies'}</li>`;
        }
        if (hasSqlInjection) {
          const count = node.code_smells?.filter(smell => getCategory(smell) === 'sql_injection').length || 0;
          tooltipContent += `<li class="text-red-800 font-medium">• ${escapeHtml(String(count))} potential SQL injection risk${count === 1 ? '' : 's'}</li>`;
        }
        if (hasComplexity) {
          const complexity = node.metrics?.complexity || 0;
          const cognitiveComplexity = node.metrics?.cognitive_complexity || 0;
          if (complexity > 10) tooltipContent += `<li class="text-orange-700">• High cyclomatic complexity (${complexity})</li>`;
          if (cognitiveComplexity > 15) tooltipContent += `<li class="text-orange-700">• High cognitive complexity (${cognitiveComplexity})</li>`;
        }
        if (hasStyleIssues) {
          const count = node.code_smells?.filter(smell => getCategory(smell) === 'style').length || 0;
          tooltipContent += `<li class="text-blue-700">• ${escapeHtml(String(count))} style issue${count === 1 ? '' : 's'}</li>`;
        }
        const otherIssues = node.code_smells?.filter(smell =>
          !['security', 'sql_injection', 'style'].includes(getCategory(smell))) || [];
        if (otherIssues.length > 0) {
          tooltipContent += `<li class="text-gray-700">• ${escapeHtml(String(otherIssues.length))} other code quality issues</li>`;
        }
        tooltipContent += `
            </ul>
          </div>
        `;
      }
    
      if (node.docstring) {
        tooltipContent += `
          <div class="mt-2 p-2 bg-green-50 border-l-3 border-green-500 rounded text-xs text-green-800 italic">
            ${escapeHtml(node.docstring)}
          </div>
        `;
      }
    
      if (node.type === 'class' && node.methods) {
        tooltipContent += `
          <div class="mt-2">
            <div class="text-xs font-semibold text-cyan-700 mb-1">Methods</div>
            <ul class="text-xs space-y-0.5 pl-2">
        `;
        let methodsShown = 0;
        for (const [methodName] of Object.entries(node.methods)) {
          if (methodsShown < 3) {
            tooltipContent += `<li class="flex items-center"><span class="text-cyan-500 mr-1">○</span> ${escapeHtml(methodName)}</li>`;
            methodsShown++;
          }
        }
        if (Object.keys(node.methods).length > 3) {
          tooltipContent += `<li class="text-gray-500 italic text-xs">...and ${Object.keys(node.methods).length - 3} more</li>`;
        }
        tooltipContent += `
            </ul>
          </div>
        `;
      }
    
      if (node.metrics) {
        tooltipContent += `
          <div class="mt-2 grid grid-cols-3 gap-2 text-xs">
        `;
        if (node.metrics.lines) {
          tooltipContent += `
            <div class="bg-gray-50 p-2 rounded text-center">
              <div class="text-gray-500">Lines</div>
              <div class="font-bold text-gray-800">${escapeHtml(String(node.metrics.lines))}</div>
            </div>
          `;
        }
        if (node.metrics.functions) {
          tooltipContent += `
            <div class="bg-gray-50 p-2 rounded text-center">
              <div class="text-gray-500">Functions</div>
              <div class="font-bold text-gray-800">${escapeHtml(String(node.metrics.functions))}</div>
            </div>
          `;
        }
        if (node.metrics.classes) {
          tooltipContent += `
            <div class="bg-gray-50 p-2 rounded text-center">
              <div class="text-gray-500">Classes</div>
              <div class="font-bold text-gray-800">${escapeHtml(String(node.metrics.classes))}</div>
            </div>
          `;
        }
        tooltipContent += `
          </div>
        `;
      }
    
      const connectedNodes = connectionsMap.get(node.id) || new Set();
      if (connectedNodes.size > 0) {
        tooltipContent += `
          <div class="mt-2 flex items-center justify-between border-t border-gray-100 pt-2">
            <div class="text-xs text-gray-500">
              <span class="font-medium text-gray-700">${connectedNodes.size}</span> connections
            </div>
            <div class="text-xs text-indigo-600 font-medium">Click for details</div>
          </div>
        `;
      }
    
      tooltipContent += `</div>`;
      node.tooltipContent = tooltipContent; 
    });

    let isZooming = false;
    zoom.on('start', () => { isZooming = true; })
    .on('end', () => { 
      setTimeout(() => { isZooming = false; }, 200);
    });

    nodeSelection
      .on('mouseover', (event, d) => {
        if (isZooming) return;
        const connectedNodes = connectionsMap.get(d.id) || new Set();

        d3.select(event.currentTarget)
          .select('circle')
          .attr('r', getNodeSize(d) * 1.2)
          .attr('stroke-width', '3px');

          tooltip.html(d.tooltipContent || '')
          .style('left', `${event.pageX + 15}px`)
          .style('top', `${event.pageY + 15}px`)
          .transition()
          .duration(200)
          .style('opacity', 0.98)
          .style('transform', 'translateY(0px)');

        nodeSelection.style('opacity', n => {
          return n.id === d.id || connectedNodes.has(n.id) ? 1 : 0.2;
        });

        linkSelection.style('opacity', l => {
          const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
          const targetId = typeof l.target === 'string' ? l.target : l.target.id;
          return sourceId === d.id || targetId === d.id ? 1 : 0.15;
        });
      })
      .on('mouseout', (event, d) => {
        d3.select(event.currentTarget)
          .select('circle')
          .attr('r', getNodeSize(d))
          .attr('stroke-width', '2px');

        tooltip.transition()
          .duration(200)
          .style('opacity', 0)
          .style('transform', 'translateY(10px)');

        nodeSelection.style('opacity', 1);
        linkSelection.style('opacity', 0.7);
      })
      .on('click', (_, d) => navigate(`/node/${d.id}`));

    const ticked = () => {
      requestAnimationFrame(() => {
        linkSelection.attr('d', d => {
          const source = typeof d.source === 'string' ? nodeDataByIdRef.current.get(d.source) || { x: 0, y: 0 } : d.source;
          const target = typeof d.target === 'string' ? nodeDataByIdRef.current.get(d.target) || { x: 0, y: 0 } : d.target;
          return `M${source.x},${source.y}L${target.x},${target.y}`;
        });
        nodeSelection.attr('transform', d => `translate(${d.x || 0},${d.y || 0})`);
      });
    };

    simulation.on('tick', ticked);
    simulation.force<d3.ForceLink<CodeNode, CodeLink>>('link')?.links(data.links);
  
    setTimeout(() => {
      if (!svgRef.current || !zoomRef.current) return;
      const bounds = (g.node() as SVGGElement)?.getBBox();
      if (bounds) {
        const dx = bounds.width;
        const dy = bounds.height;
        const x = bounds.x + (dx / 2);
        const y = bounds.y + (dy / 2);
        const scale = Math.min(0.9, 0.9 / Math.max(dx / width, dy / height));
        const translate = [width / 2 - scale * x, height / 2 - scale * y];
        svg.transition()
          .duration(750)
          .call(zoomRef.current.transform, d3.zoomIdentity
            .translate(translate[0], translate[1])
            .scale(scale));
      }
    }, 500);
  
    return () => {
      tooltip.remove();
      if (simulationRef.current) simulationRef.current.stop();
    };
  }, [data, width, height, navigate, getNodeSize, getNodeFillColor, getNodeStrokeColor, getCategory]);

  const resetZoom = () => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current)
        .transition()
        .duration(750)
        .call(zoomRef.current.transform, d3.zoomIdentity);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    const nodeSelection = svg.selectAll('.node');
    const linkSelection = svg.selectAll('path');
    
    if (term === '') {
      nodeSelection.transition().duration(300).style('opacity', 1);
      linkSelection.transition().duration(300).style('opacity', 0.7);
      return;
    }
    
    const matchedNodes = new Set<string>();
    
    data.nodes.forEach(node => {
      if (node.id && typeof node.id !== 'string') {
      }
      
      if ((node.name && typeof node.name === 'string' && node.name.toLowerCase().includes(term.toLowerCase())) ||
          (node.id && typeof node.id === 'string' && node.id.toLowerCase().includes(term.toLowerCase()))) {
        matchedNodes.add(node.id);
      }
    });
        
    nodeSelection.transition().duration(300).style('opacity', (d: any) => {
      return matchedNodes.has(d.id) ? 1 : 0.1;
    });
    

  linkSelection.transition().duration(300).style('opacity', (d: any) => {
    if (!d || d.source === undefined || d.target === undefined) {
      console.warn('Invalid link data found:', d);
      return 0.1; 
    }
    
    try {
      let sourceId = null;
      let targetId = null;
      
      if (typeof d.source === 'string') {
        sourceId = d.source;
      } else if (d.source && typeof d.source === 'object' && d.source.id !== undefined) {
        sourceId = d.source.id;
      }
      
      if (typeof d.target === 'string') {
        targetId = d.target;
      } else if (d.target && typeof d.target === 'object' && d.target.id !== undefined) {
        targetId = d.target.id;
      }
      
      if (sourceId === null || targetId === null) {
        return 0.1;
      }
      
      return (matchedNodes.has(sourceId) || matchedNodes.has(targetId)) ? 0.7 : 0.1;
      } catch (error) {
        console.error('Error processing link data:', error, d);
        return 0.1; 
        }
      }
    );
    }
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
          <div className="text-lg font-medium text-gray-700">Loading visualization data...</div>
          <div className="text-sm text-gray-500 mt-2">This may take a moment</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="max-w-md w-full p-8 bg-white rounded-xl shadow-lg">
          <div className="flex justify-center mb-6">
            <div className="rounded-full bg-red-100 p-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <h2 className="text-xl font-semibold text-center text-gray-800 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 text-center mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium shadow-md hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative w-full h-screen overflow-hidden bg-gray-50">
      <div className="fixed top-0 left-0 right-0 z-10 backdrop-blur-md bg-white bg-opacity-80 border-b border-gray-200 shadow-sm">
        <div className="max-w-full mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-lg font-semibold text-indigo-600"> Treeline </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                  </svg>
                </div>
                <input
                  type="text"
                  id="search"
                  placeholder="Search nodes..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="w-64 pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none placeholder-gray-400 text-sm"
                />
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={resetZoom}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                </svg>
                Reset View
              </button>
              
              <button
                onClick={() => setShowLegend(!showLegend)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                {showLegend ? 'Hide Legend' : 'Show Legend'}
              </button>
              
              <button
                onClick={() => navigate('/project-metrics')}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zm6-4a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zm6-3a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
                View Metrics
              </button>
            </div>
          </div>
        </div>
      </div>

      {showLegend && (
        <div className="fixed bottom-5 left-5 bg-white rounded-xl shadow-lg z-10 p-5 border border-gray-100 w-64 transition-all duration-300 ease-in-out">
          <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-500" viewBox="0 0 20 20" fill="currentColor">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Legend
          </h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Node Types</p>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex items-center text-xs">
                  <div className="w-4 h-4 rounded-full bg-blue-500 mr-2 border border-white shadow-sm"></div>
                  <span className="text-gray-700">Module</span>
                </div>
                <div className="flex items-center text-xs">
                  <div className="w-4 h-4 rounded-full bg-amber-400 mr-2 border border-white shadow-sm"></div>
                  <span className="text-gray-700">Entry Point</span>
                </div>
                <div className="flex items-center text-xs">
                  <div className="w-4 h-4 rounded-full bg-cyan-600 mr-2 border border-white shadow-sm"></div>
                  <span className="text-gray-700">Class</span>
                </div>
                <div className="flex items-center text-xs">
                  <div className="w-4 h-4 rounded-full bg-teal-600 mr-2 border border-white shadow-sm"></div>
                  <span className="text-gray-700">Function</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Connection Types</p>
              <div className="space-y-2">
                <div className="flex items-center text-xs">
                  <div className="w-8 h-0.5 bg-purple-600 mr-2"></div>
                  <span className="text-gray-700">Imports</span>
                </div>
                <div className="flex items-center text-xs">
                  <div className="w-8 h-0.5 bg-green-600 mr-2"></div>
                  <span className="text-gray-700">Contains</span>
                </div>
                <div className="flex items-center text-xs">
                  <div className="w-8 h-0.5 bg-orange-600 mr-2"></div>
                  <span className="text-gray-700">Calls</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Issues</p>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex items-center text-xs">
                  <div className="w-4 h-4 rounded-full bg-red-400 mr-2 border border-white shadow-sm"></div>
                  <span className="text-gray-700">High Complexity</span>
                </div>
                <div className="flex items-center text-xs">
                  <div className="w-4 h-4 rounded-full bg-red-500 mr-2 border border-white shadow-sm"></div>
                  <span className="text-gray-700">Security Issue</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-500">
              Hover over nodes to see details and click to view code.
            </p>
          </div>
        </div>
      )}

      <svg ref={svgRef} id="visualization" className="w-full h-screen pt-14"></svg>
      
      <div className="fixed top-20 right-5 bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-md z-10 p-4 border border-gray-100">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Stats</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col">
            <span className="text-xs text-gray-500">Nodes</span>
            <span className="text-lg font-semibold text-gray-800">{data.nodes.length}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-gray-500">Connections</span>
            <span className="text-lg font-semibold text-gray-800">{data.links.length}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-gray-500">Classes</span>
            <span className="text-lg font-semibold text-gray-800">
              {data.nodes.filter(n => n.type === 'class').length}
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-gray-500">Functions</span>
            <span className="text-lg font-semibold text-gray-800">
              {data.nodes.filter(n => n.type === 'function').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualizationPage;