import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import * as d3 from 'd3';
import { GraphData, CodeNode, CodeSmell } from '../types';
import { fetchGraphData } from '../services/dataServices';
import { debounce } from 'lodash';

interface TreeNode {
  id: string;
  name: string;
  children: TreeNode[];
  [key: string]: any;
}

const VisualizationPage: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [isRadial, setIsRadial] = useState<boolean>(false);
  const [isHierarchical, setIsHierarchical] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [width, setWidth] = useState<number>(window.innerWidth);
  const [height, setHeight] = useState<number>(window.innerHeight);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  const simulationRef = useRef<d3.Simulation<any, any> | null>(null);
  const gRef = useRef<d3.Selection<SVGGElement, unknown, null, undefined> | null>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  
  const nodeDataByIdRef = useRef<Map<string, CodeNode>>(new Map());
  const canvasRef = useRef<HTMLCanvasElement>(null);

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
        if (endIndex !== -1) {
          return smell.slice(1, endIndex).toLowerCase();
        }
      }
      return 'unknown';
    } else if (typeof smell === 'object' && smell.category) {
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
        graphData.nodes.forEach(node => {
          nodeMap.set(node.id, node);
        });
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
  
  const setHierarchicalLayout = () => {
    setIsHierarchical(!isHierarchical);
    
    if (isHierarchical) {
      if (simulationRef.current && gRef.current) {
        gRef.current.transition().duration(750).attr('transform', '');
        simulationRef.current.alpha(1).restart();
      }
      return;
    }
    
    if (gRef.current && data.nodes.length > 0 && simulationRef.current) {
      simulationRef.current.stop();
      
      const rootNodes = data.nodes.filter(n => n.type === 'module' && 
        !data.links.some(l => l.type === 'contains' && 
          (typeof l.target === 'object' ? l.target.id : l.target) === n.id
        )
      );
      
      function buildTree(node: CodeNode): TreeNode {
        const children = data.links
          .filter(l => l.type === 'contains' && 
            (typeof l.source === 'object' ? l.source.id : l.source) === node.id
          )
          .map(l => {
            const targetId = typeof l.target === 'object' ? l.target.id : l.target;
            return data.nodes.find(n => n.id === targetId) || {} as CodeNode;
          });
          
        const result: TreeNode = {
          id: node.id,
          name: node.name,
          children: children.map(buildTree)
        };
        
        Object.keys(node).forEach(key => {
          if (key !== 'id' && key !== 'name' && key !== 'children') {
            result[key] = (node as any)[key];
          }
        });
        
        return result;
      }
      
      
      const hierarchicalData: TreeNode = { 
        id: 'root', 
        name: 'root', 
        children: rootNodes.map(buildTree)
      };
      
      const root = d3.hierarchy(hierarchicalData);
      const treeLayout = d3.tree<TreeNode>().size([height * 3, width - 200]);
      treeLayout(root);

      root.descendants().forEach(d => {
        if (!d.data.id) return;
        const original = data.nodes.find(n => n.id === d.data.id);
        if (original) {
          original.x = d.y;
          original.y = d.x;
        }
      });
      
      const nodeSelection = d3.select(svgRef.current)
        .select('g')
        .selectAll('.node');
      
      const linkSelection = d3.select(svgRef.current)
        .select('g')
        .selectAll('path');
      
      nodeSelection.transition()
        .duration(750)
        .attr('transform', d => `translate(${(d as any).x},${(d as any).y})`);
      
      linkSelection.transition()
        .duration(750)
        .attr('d', d => {
          const source = typeof (d as any).source === 'object' ? (d as any).source : { x: 0, y: 0 };
          const target = typeof (d as any).target === 'object' ? (d as any).target : { x: 0, y: 0 };
          
          if ((d as any).type === 'contains') {
            return `M${source.x},${source.y}
                    C${source.x},${(source.y + target.y) / 2}
                    ${target.x},${(source.y + target.y) / 2}
                    ${target.x},${target.y}`;
          }
          return `M${source.x},${source.y}L${target.x},${target.y}`;
        });
        
      const bounds = {
        left: Math.min(...data.nodes.map(n => n.x || 0)),
        right: Math.max(...data.nodes.map(n => n.x || 0)),
        top: Math.min(...data.nodes.map(n => n.y || 0)),
        bottom: Math.max(...data.nodes.map(n => n.y || 0))
      };
      
      const centerX = width / 2 - (bounds.left + (bounds.right - bounds.left) / 2);
      const centerY = height / 2 - (bounds.top + (bounds.bottom - bounds.top) / 2);
      
      gRef.current.transition()
        .duration(750)
        .attr('transform', `translate(${centerX},${centerY})`);
    }
  };
  
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
      .on('zoom', (event) => {
        g.attr('transform', event.transform.toString());
      });
    
    zoomRef.current = zoom;
    svg.call(zoom);
    
    const tooltip = d3.select(containerRef.current)
      .append('div')
      .attr('class', 'absolute p-3 bg-white rounded-lg shadow-md pointer-events-none text-sm max-w-xs opacity-0 z-50')
      .style('z-index', '1000');
    

    // const useCanvas = data.nodes.length > 1000;
    // const ticksPerRender = data.nodes.length > 500 ? 10 : 1;
    const initialAlphaDecay = data.nodes.length > 1000 ? 0.1 : 0.05;
    const chargeStrength = Math.min(-400, -30000 / Math.sqrt(data.nodes.length));
    

    const simulation = d3.forceSimulation<any, any>()
      .nodes(data.nodes)
      .force('link', d3.forceLink().id((d: any) => d.id).distance(100).strength(0.5))
      .force('charge', d3.forceManyBody().strength(chargeStrength).distanceMax(500))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(25))
      .force('x', d3.forceX(width / 2).strength(0.05))
      .force('y', d3.forceY(height / 2).strength(0.05))
      .alphaDecay(initialAlphaDecay)
      .velocityDecay(0.4);
    
    simulationRef.current = simulation;
    
    const linkSelection = g.append('g').selectAll('path')
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
    
    const nodeSelection = g.append('g').selectAll('.node')
      .data(data.nodes)
      .join('g')
      .attr('class', d => `node node-${d.type}`)
      .style('cursor', 'pointer');
    
    const dragBehavior = d3.drag<any, any>()
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
    
    nodeSelection.call(dragBehavior);
    
    nodeSelection.append('rect')
      .attr('class', 'text-background')
      .attr('fill', 'white')
      .attr('fill-opacity', 0.9)
      .attr('rx', 3)
      .attr('ry', 3);
    
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
      .style('fill', '#333')
      .each(function() {
        const bbox = (this as SVGTextElement).getBBox();
        const parent = this.parentNode as Element;
        d3.select(parent)
          .select('rect.text-background')
          .attr('x', bbox.x - 4)
          .attr('y', bbox.y - 2)
          .attr('width', bbox.width + 8)
          .attr('height', bbox.height + 4);
      });
    
    nodeSelection.on('mouseover', function(event, d) {
      const connections = data.links.filter(l => 
        (typeof l.source === 'object' ? l.source.id : l.source) === d.id || 
        (typeof l.target === 'object' ? l.target.id : l.target) === d.id
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
          tooltipContent += `• <span style="color: #b91c1c;">${escapeHtml(String(count))} security vulnerability${count === 1 ? '' : 'ies'} detected!</span><br>`;        }
        
        if (hasSqlInjection) {
          const count = d.code_smells?.filter(smell => getCategory(smell) === 'sql_injection').length || 0;
          tooltipContent += `• <span style="color: #b91c1c;">${escapeHtml(String(count))} potential SQL injection risk${count === 1 ? '' : 's'}!</span><br>`;        }
        
        if (hasComplexity) {
          let complexity = d.metrics?.complexity || 0;
          let cognitiveComplexity = d.metrics?.cognitive_complexity || 0;
          
          if (complexity > 10) {
            tooltipContent += `• <span style="color: #b91c1c;">High cyclomatic complexity (${complexity})</span><br>`;
          }
          
          if (cognitiveComplexity > 15) {
            tooltipContent += `• <span style="color: #b91c1c;">High cognitive complexity (${cognitiveComplexity})</span><br>`;
          }
        }
        
        if (hasStyleIssues) {
          const count = d.code_smells?.filter(smell => getCategory(smell) === 'style').length || 0;
          tooltipContent += `• <span style="color: #0369a1;">${escapeHtml(String(count))} style issue${count === 1 ? '' : 's'}</span><br>`;
        }
        
        const otherIssues = d.code_smells ? d.code_smells.filter(smell => 
          getCategory(smell) !== 'security' && 
          getCategory(smell) !== 'sql_injection' && 
          getCategory(smell) !== 'style') : [];
          
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
        for (const [methodName, _] of Object.entries(d.methods)) {
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
        if (d.metrics.lines) {
          tooltipContent += `• Lines: ${escapeHtml(String(d.metrics.lines))}<br>`;
        }
        if (d.metrics.functions) {
          tooltipContent += `• Functions: ${escapeHtml(String(d.metrics.functions))}<br>`;
        }
        if (d.metrics.classes) {
          tooltipContent += `• Classes: ${escapeHtml(String(d.metrics.classes))}<br>`;
        }
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
      
      nodeSelection.style('opacity', n => (n as any).id === d.id || connections.some(c => 
        (typeof c.source === 'object' ? c.source.id : c.source) === (n as any).id || 
        (typeof c.target === 'object' ? c.target.id : c.target) === (n as any).id
      ) ? 1 : 0.1);
      
      linkSelection.style('opacity', l => 
        (typeof l.source === 'object' ? l.source.id : l.source) === d.id || 
        (typeof l.target === 'object' ? l.target.id : l.target) === d.id ? 1 : 0.1
      );
    })
    .on('mouseout', function() {
      tooltip.transition()
        .duration(500)
        .style('opacity', 0);
      
      nodeSelection.style('opacity', 1);
      linkSelection.style('opacity', 0.7);
    })
    .on('click', (_, d) => {
      navigate(`/node/${d.id}`);
    });
    
    let tickCounter = 0;
    const ticksPerRender = data.nodes.length > 500 ? 5 : 1;

    const ticked = () => {
      tickCounter++;
      
      const nodeCount = data.nodes.length;
      const adaptiveTicksPerRender = 
        nodeCount > 2000 ? 20 :
        nodeCount > 1000 ? 15 :
        nodeCount > 500 ? 10 :
        nodeCount > 250 ? 5 : 1;
      
      if (tickCounter % adaptiveTicksPerRender !== 0) return;
      
      const alpha = simulationRef.current?.alpha() || 0;
      if (nodeCount > 1000 && alpha > 0.1) return;
      
      const currentNodeSelection = nodeSelection;
      const currentLinkSelection = linkSelection;
      
      if (!currentNodeSelection || !currentLinkSelection) return;
      
      if (!svgRef.current) return;
      
      window.requestAnimationFrame(() => {
        if (!svgRef.current) return;
        
        try {
          currentLinkSelection.attr('d', (d: any) => {
            const source = typeof d.source === 'object' ? d.source : { x: 0, y: 0 };
            const target = typeof d.target === 'object' ? d.target : { x: 0, y: 0 };
            return `M${source.x},${source.y}L${target.x},${target.y}`;
          });
          
          currentNodeSelection.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
        } catch (e) {
          console.debug('D3 update skipped - component may be updating');
        }
      });
    };

    if (data.nodes.length > 500 && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
  
      if (ctx) {
        canvas.width = width;
        canvas.height = height;
  
        const canvasTicked = () => {
          tickCounter++;
          if (tickCounter % ticksPerRender !== 0) return;
  
          ctx.clearRect(0, 0, width, height);
  
          const transform = d3.zoomTransform(svg.node() as Element);
          ctx.save();
          ctx.translate(transform.x, transform.y);
          ctx.scale(transform.k, transform.k);
  
          data.links.forEach(link => {
            const source = typeof link.source === 'object' ? link.source : { x: 0, y: 0 };
            const target = typeof link.target === 'object' ? link.target : { x: 0, y: 0 };
  
            ctx.beginPath();
            ctx.moveTo(source.x ?? 0, source.y ?? 0);
            ctx.lineTo(target.x ?? 0, target.y ?? 0);
  
            ctx.strokeStyle = link.type === 'imports' ? '#7c3aed' :
                             link.type === 'contains' ? '#059669' : '#ea580c';
            ctx.globalAlpha = 0.7;
            ctx.lineWidth = 1.5;
            ctx.stroke();
          });
  
          data.nodes.forEach(node => {
            const size = getNodeSize(node);
  
            ctx.beginPath();
            ctx.arc(node.x ?? 0, node.y ?? 0, size, 0, Math.PI * 2);
            ctx.fillStyle = getNodeFillColor(node);
            ctx.fill();
            ctx.strokeStyle = getNodeStrokeColor(node);
            ctx.lineWidth = 2;
            ctx.stroke();
  
            if (node.type === 'module' || node.is_entry) {
              ctx.font = '10px "Segoe UI", sans-serif';
              ctx.fillStyle = '#333';
              ctx.fillText(node.name, node.x ?? 0 + size + 5, node.y ?? 0 + 4);
            }
          });
  
          ctx.restore();
        };
  
        simulation.on('tick', canvasTicked);
  
        canvas.addEventListener('click', (event) => {
          const transform = d3.zoomTransform(svg.node() as Element);
          const x = (event.offsetX - transform.x) / transform.k;
          const y = (event.offsetY - transform.y) / transform.k;
  
          const clickedNode = data.nodes.find(node => {
            const size = getNodeSize(node) + 5; 
            return Math.abs(node.x ?? 0 - x) < size && Math.abs(node.y ?? 0 - y) < size;
          });
  
          if (clickedNode) {
            navigate(`/node/${clickedNode.id}`);
          }
        });
  
        svg.style('pointer-events', 'none');
        canvas.style.display = 'block';
        canvas.style.pointerEvents = 'auto';
        g.style('display', 'none');
  
        zoom.on('zoom', (event) => {
          g.attr('transform', event.transform.toString());
          canvasTicked(); 
        });
      }
    } else {
      simulation.on('tick', ticked);
      if (canvasRef.current) {
        canvasRef.current.style.display = 'none';
      }
      svg.style('pointer-events', 'auto');
      g.style('display', 'block');
    }

    simulation
      .nodes(data.nodes)
      .on('tick', ticked);
    
    const linkForce = simulation.force('link') as d3.ForceLink<any, any>;
    if (linkForce) {
      linkForce.links(data.links);
    }
    
    const collisionForce = simulation.force('collision') as d3.ForceCollide<any>;
    if (collisionForce) {
      collisionForce.radius((d: any) => {
        return d.type === 'module' ? 60 : d.type === 'class' ? 50 : 40;
      }).strength(0.8);
    }
    
    return () => {
      tooltip.remove();
      if (simulationRef.current) {
        simulationRef.current.stop();
      }
    };
  }, [data, width, height, navigate]);
  
  const resetZoom = () => {
    if (svgRef.current && zoomRef.current && gRef.current) {
      const zoom = zoomRef.current as unknown as d3.ZoomBehavior<Element, unknown>;
      d3.select(svgRef.current)
        .transition()
        .duration(750)
        .call(zoom.transform as any, d3.zoomIdentity);
    }
  };
  
  const toggleLayout = () => {
    setIsRadial(!isRadial);
    
    if (simulationRef.current) {
      const simulation = simulationRef.current;
      
      if (!isRadial) {
        simulation.force('x', null);
        simulation.force('y', null);
        simulation.force('r', d3.forceRadial(250, width / 2, height / 2));
        simulation.force('charge', d3.forceManyBody().strength(-100));
      } else {
        simulation.force('r', null);
        simulation.force('x', d3.forceX(width / 2).strength(0.1));
        simulation.force('y', d3.forceY(height / 2).strength(0.1));
        simulation.force('charge', d3.forceManyBody().strength(-1000));
      }
      
      simulation.alpha(1).restart();
    }
  };
  
  const debouncedSearch = useCallback(
    debounce((term: string) => {
      if (!svgRef.current) return;
      
      const svg = d3.select(svgRef.current);
      const nodeSelection = svg.selectAll('.node');
      const linkSelection = svg.selectAll('path');
      
      if (term === "") {
        nodeSelection.style("opacity", 1);
        linkSelection.style("opacity", 0.7);
        return;
      }
      
      const lowerTerm = term.toLowerCase();
      const matchedNodes = new Set<string>();
      
      data.nodes.forEach(node => {
        if (node.name.toLowerCase().includes(lowerTerm)) {
          matchedNodes.add(node.id);
          
          data.links.forEach(l => {
            const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
            const targetId = typeof l.target === 'object' ? l.target.id : l.target;
            
            if (sourceId === node.id) matchedNodes.add(targetId);
            if (targetId === node.id) matchedNodes.add(sourceId);
          });
        }
      });
      
      nodeSelection.style("opacity", (d: any) => matchedNodes.has((d as CodeNode).id) ? 1 : 0.1);
      
      linkSelection.style("opacity", (d: any) => {
        const sourceId = typeof d.source === 'object' ? d.source.id : d.source;
        const targetId = typeof d.target === 'object' ? d.target.id : d.target;
        
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
          <button 
            onClick={toggleLayout}
            className="bg-blue-700 text-white border-none px-4 py-2 rounded-md cursor-pointer text-sm transition-colors hover:bg-blue-800"
          >
            Toggle Layout
          </button>
          <button 
            onClick={setHierarchicalLayout}
            className="bg-blue-700 text-white border-none px-4 py-2 rounded-md cursor-pointer text-sm transition-colors hover:bg-blue-800"
          >
            {isHierarchical ? 'Force Layout' : 'Hierarchical View'}
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
      
      <canvas 
        ref={canvasRef}
        style={{ 
          display: data.nodes.length > 500 ? 'block' : 'none',
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none'
        }}
      />

      <svg ref={svgRef} id="visualization" className="w-full h-screen"></svg>
    </div>
  );
};

export default VisualizationPage;