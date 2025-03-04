import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchNodeData } from '../services/dataServices';
import ComplexityTimeline from '../components/ComplexityTimeline';
import ImpactAnalysis from '../components/ImpactAnalysis';
import CodeMetricsGraphs from '../components/CodeMetricsGraphs';
import * as d3 from 'd3';
import { 
  fetchDetailedMetrics, 
  fetchIssuesByCategory,
  fetchComplexityBreakdown 
} from '../services/dataServices';

interface NodeDetails {
  node: any;
  connections: {
    incoming: any[];
    outgoing: any[];
  };
  file_content: string | null;
}

const NodeDetailsPage: React.FC = () => {
  const { nodeId } = useParams<{ nodeId: string }>();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [nodeData, setNodeData] = useState<NodeDetails | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [projectMetrics, setProjectMetrics] = useState<any>(null);
  const [complexityBreakdown, setComplexityBreakdown] = useState<any>(null);
  const [issuesByCategory, setIssuesByCategory] = useState<any>(null);
  const [loadingProjectMetrics, setLoadingProjectMetrics] = useState<boolean>(false);
  const donutChartRef = useRef<SVGSVGElement>(null);
  const barChartRef = useRef<SVGSVGElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (activeTab === 'project_metrics' && !projectMetrics) {
      const fetchProjectData = async () => {
        try {
          setLoadingProjectMetrics(true);
          const [metricsData, complexityData, issuesData] = await Promise.all([
            fetchDetailedMetrics(),
            fetchComplexityBreakdown(),
            fetchIssuesByCategory()
          ]);
          
          setProjectMetrics(metricsData);
          setComplexityBreakdown(complexityData);
          setIssuesByCategory(issuesData);
        } catch (err) {
          console.error('Error fetching project metrics:', err);
        } finally {
          setLoadingProjectMetrics(false);
        }
      };
      
      fetchProjectData();
    }
  }, [activeTab, projectMetrics]);
  
  // Add these D3 rendering effects
  useEffect(() => {
    if (donutChartRef.current && activeTab === 'project_metrics' && issuesByCategory?.category_counts) {
      renderIssuesDonutChart();
    }
  }, [issuesByCategory, activeTab, donutChartRef.current]);
  
  useEffect(() => {
    if (barChartRef.current && activeTab === 'project_metrics' && complexityBreakdown?.total) {
      renderComplexityBarChart();
    }
  }, [complexityBreakdown, activeTab, barChartRef.current]);
  
  // Add these rendering functions
  const renderIssuesDonutChart = () => {
    if (!donutChartRef.current || !issuesByCategory?.category_counts) return;
    
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
    
    const issueData = Object.entries(issuesByCategory.category_counts).map(
      ([name, value]) => ({ name, value: value as number })
    );
    
    const categoryColors: {[key: string]: string} = {
      'security': '#ef4444',
      'style': '#3b82f6', 
      'duplication': '#10b981',
      'code_smells': '#f59e0b',
      'complexity': '#8b5cf6',
      'sql_injection': '#ec4899'
    };
    
    const color = d3.scaleOrdinal<string>()
      .domain(issueData.map(d => d.name))
      .range(issueData.map(d => categoryColors[d.name] || '#6b7280'));
    
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
      .data(pie(issueData))
      .enter()
      .append('path')
      .attr('d', arc as any)
      .attr('fill', d => color(d.data.name) as string)
      .attr('stroke', 'white')
      .style('stroke-width', '2px')
      .style('opacity', 0.7);
    
    arcs.append('title')
      .text(d => `${d.data.name}: ${d.data.value} issues (${Math.round(d.data.value/issueData.reduce((a, b) => a + b.value, 0)*100)}%)`);
    
    svg.selectAll('allPolylines')
      .data(pie(issueData))
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
      .data(pie(issueData))
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
    
    const totalIssues = issueData.reduce((sum, item) => sum + item.value, 0);
    
    svg.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .text(`${totalIssues} Issues`);
  };
  
  const renderComplexityBarChart = () => {
    if (!barChartRef.current || !complexityBreakdown?.total) return;
    
    d3.select(barChartRef.current).selectAll('*').remove();
    
    const width = 450;
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 70, left: 90 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    const svg = d3.select(barChartRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const data = Object.entries(complexityBreakdown.total)
      .map(([name, value]) => ({
        name: name.replace(/_/g, ' '),
        value: value as number
      }))
      .filter(item => item.value > 0)
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
    
    const x = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value) as number])
      .range([0, innerWidth]);
    
    const y = d3.scaleBand()
      .domain(data.map(d => d.name))
      .range([0, innerHeight])
      .padding(0.2);
    
    svg.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x));
    
    svg.append('g')
      .call(d3.axisLeft(y));
    
    svg.selectAll('bars')
      .data(data)
      .enter()
      .append('rect')
      .attr('y', d => y(d.name) as number)
      .attr('x', 0)
      .attr('height', y.bandwidth())
      .attr('width', d => x(d.value))
      .attr('fill', '#3b82f6');
      
    svg.selectAll('bar-values')
      .data(data)
      .enter()
      .append('text')
      .attr('y', d => (y(d.name) as number) + y.bandwidth() / 2 + 4)
      .attr('x', d => x(d.value) + 5)
      .attr('text-anchor', 'start')
      .text(d => d.value)
      .style('font-size', '12px');
    
    svg.append('text')
      .attr('x', innerWidth / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text('Top Complexity Factors');
  };

  useEffect(() => {
    const loadNodeData = async () => {
      if (!nodeId) return;
      
      try {
        setLoading(true);
        const data = await fetchNodeData(nodeId);
        setNodeData(data);
        setError(null);
      } catch (err) {
        console.error('Error loading node data:', err);
        setError('Failed to load node details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    loadNodeData();
  }, [nodeId]);

  const renderMetricsGraphs = (node: any) => {
    if (!node.metrics) {
      return (
        <div className="bg-gray-50 border-l-4 border-gray-300 p-4 rounded-r-md mb-6">
          <p className="text-gray-700">Not enough data available for metrics visualizations.</p>
        </div>
      );
    }
    
    return (
      <div className="bg-white shadow-md rounded-xl p-6 mb-6">
        <h3 className="text-purple-600 font-semibold text-lg flex items-center mb-4">
          <span className="mr-2">📊</span>
          Code Quality Visualizations
        </h3>
        <CodeMetricsGraphs 
          metrics={node.metrics}
          codeSmells={node.code_smells || []}
        />
      </div>
    );
  };

  const getNodeTypePillClass = (type: string) => {
    switch (type) {
      case 'module': return 'bg-blue-100 text-blue-800';
      case 'class': return 'bg-cyan-100 text-cyan-800';
      case 'function': return 'bg-teal-100 text-teal-800';
      default: return '';
    }
  };

  const formatIssues = (issues: any[]) => {
    if (!issues || issues.length === 0) {
      return null;
    }

    return (
      <div className="mb-6">
        <h3 className="text-red-600 font-semibold text-lg flex items-center mb-2">
          <span className="mr-2">⚠️</span>
          Issues ({issues.length})
        </h3>
        <ul className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-md">
          {issues.map((issue, index) => (
            <li key={index} className="mb-2 last:mb-0 flex items-start">
              <span className="mr-2">•</span>
              <span>{typeof issue === 'string' ? issue : issue.description || issue.message}</span>
              {(issue.line || issue.lineno) && 
                <span className="text-gray-600 text-sm ml-auto">Line {issue.line || issue.lineno}</span>
              }
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  const formatMetrics = (metrics: any) => {
    if (!metrics) return null;
    
    return (
      <div className="mb-6">
        <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-2">
          <span className="mr-2">📊</span>
          Metrics
        </h3>
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-md">
          <table className="w-full">
            <tbody>
              {Object.entries(metrics).map(([key, value]) => {
                if (key.startsWith('_')) return null;
                
                const formattedKey = key
                  .replace(/_/g, ' ')
                  .replace(/\b\w/g, c => c.toUpperCase());
                
                const isWarning = 
                  (key === 'complexity' && Number(value) > 10) ||
                  (key === 'cognitive_complexity' && Number(value) > 15) ||
                  (key === 'lines' && Number(value) > 100) ||
                  (key === 'params' && Number(value) > 5);
                
                return (
                  <tr key={key} className={isWarning ? "bg-amber-50" : ""}>
                    <td className="py-1 font-medium">{formattedKey}</td>
                    <td className={`py-1 ${isWarning ? "text-amber-700" : ""}`}>
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };
  
  const formatConnections = (connections: { incoming: any[], outgoing: any[] }) => {
    if (!connections || (connections.incoming.length === 0 && connections.outgoing.length === 0)) {
      return null;
    }
    
    return (
      <div className="mb-6">
        <h3 className="text-green-600 font-semibold text-lg flex items-center mb-2">
          <span className="mr-2">🔄</span>
          Dependencies
        </h3>
        
        {connections.incoming.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium mb-2">Incoming ({connections.incoming.length})</h4>
            <ul className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-md">
              {connections.incoming.map((link, index) => {
                const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                const sourceName = typeof link.source === 'object' ? link.source.name : link.source;
                
                return (
                  <li key={index} className="mb-2 last:mb-0">
                    <span className={`inline-block px-2.5 py-0.5 rounded text-xs mr-2 ${
                      link.type === 'imports' ? 'bg-purple-100 text-purple-800' :
                      link.type === 'contains' ? 'bg-green-100 text-green-800' :
                      'bg-orange-100 text-orange-800'
                    }`}>
                      {link.type}
                    </span>
                    from{' '}
                    <button 
                      onClick={() => navigate(`/node/${sourceId}`)}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {sourceName}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
        
        {connections.outgoing.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Outgoing ({connections.outgoing.length})</h4>
            <ul className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-md">
              {connections.outgoing.map((link, index) => {
                const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                const targetName = typeof link.target === 'object' ? link.target.name : link.target;
                
                return (
                  <li key={index} className="mb-2 last:mb-0">
                    <span className={`inline-block px-2.5 py-0.5 rounded text-xs mr-2 ${
                      link.type === 'imports' ? 'bg-purple-100 text-purple-800' :
                      link.type === 'contains' ? 'bg-green-100 text-green-800' :
                      'bg-orange-100 text-orange-800'
                    }`}>
                      {link.type}
                    </span>
                    to{' '}
                    <button 
                      onClick={() => navigate(`/node/${targetId}`)}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {targetName}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </div>
    );
  };
  
  const formatFileContent = (content: string | null) => {
    if (!content) return null;
    
    return (
      <div className="mb-6">
        <h3 className="text-gray-700 font-semibold text-lg flex items-center mb-2">
          <span className="mr-2">📄</span>
          Source Code
        </h3>
        <div className="bg-gray-800 text-gray-200 p-4 rounded-md overflow-x-auto">
          <pre className="text-sm">
            <code>{content}</code>
          </pre>
        </div>
      </div>
    );
  };

  const renderComplexityTimeline = (metrics: any) => {
    if (!metrics || !metrics.complexity || !metrics.cognitive_complexity) {
      return (
        <div className="bg-gray-50 border-l-4 border-gray-300 p-4 rounded-r-md mb-6">
          <p className="text-gray-700">Not enough complexity metrics available for timeline analysis.</p>
        </div>
      );
    }

    return (
      <div className="bg-white shadow-md rounded-xl p-6 mb-6">
        <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-4">
          <span className="mr-2">📉</span>
          Refactoring Impact Analysis
        </h3>
        <ComplexityTimeline 
          currentComplexity={metrics.complexity}
          currentCognitiveComplexity={metrics.cognitive_complexity}
          currentNestedDepth={metrics.nested_depth}
          className="w-full overflow-x-auto"
        />
      </div>
    );
  };

  const renderImpactAnalysis = (nodeData: NodeDetails) => {
    if (!nodeData || !nodeData.connections) {
      return (
        <div className="bg-gray-50 border-l-4 border-gray-300 p-4 rounded-r-md mb-6">
          <p className="text-gray-700">No connection data available for impact analysis.</p>
        </div>
      );
    }

    const { node, connections } = nodeData;
    
    return (
      <div className="bg-white shadow-md rounded-xl p-6 mb-6">
        <h3 className="text-indigo-600 font-semibold text-lg flex items-center mb-4">
          <span className="mr-2">🔄</span>
          Change Impact Analysis
        </h3>
        <ImpactAnalysis 
          nodeId={nodeId || ''}
          nodeName={node.name}
          nodeType={node.type}
          connections={connections}
          hasIssues={node.code_smells && node.code_smells.length > 0}
          highComplexity={node.metrics && (
            (node.metrics.complexity && node.metrics.complexity > 10) || 
            (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15)
          )}
        />
      </div>
    );
  };

  const renderTabs = () => {
    return (
      <div className="border-b border-gray-200 mb-6">
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'overview' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Overview
          </button>

          <button
            onClick={() => setActiveTab('project_metrics')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'project_metrics' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Project Metrics
          </button>

          <button
            onClick={() => setActiveTab('visualizations')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'visualizations' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Visualizations
          </button>

          <button
            onClick={() => setActiveTab('metrics')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'metrics' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Metrics
          </button>
          <button
            onClick={() => setActiveTab('connections')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'connections' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Dependencies
          </button>
          <button
            onClick={() => setActiveTab('refactoring')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'refactoring' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Refactoring
          </button>
          <button
            onClick={() => setActiveTab('impact')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'impact' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Impact Analysis
          </button>
          <button
            onClick={() => setActiveTab('source')}
            className={`px-4 py-2 font-medium rounded-t-lg ${
              activeTab === 'source' 
                ? 'bg-white text-blue-600 border-t border-r border-l border-gray-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Source Code
          </button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading node details...</div>
      </div>
    );
  }

  if (error || !nodeData) {
    return (
      <div className="flex items-center justify-center h-screen flex-col">
        <div className="text-xl text-red-600 mb-4">Error loading node details</div>
        <div className="text-gray-700">{error}</div>
        <button 
          onClick={() => navigate('/')}
          className="mt-6 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Back to Visualization
        </button>
      </div>
    );
  }

  const { node, connections, file_content } = nodeData;
  const hasIssues = node.code_smells && node.code_smells.length > 0;
  const highComplexity = node.metrics && (
    (node.metrics.complexity && node.metrics.complexity > 10) || 
    (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15)
  );

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-6 flex items-center justify-between">
        <button 
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          ← Back to Visualization
        </button>
        
        <div className="flex gap-2">
          {hasIssues && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-800 border border-red-300">
              <span className="mr-1">⚠️</span>
              {node.code_smells.length} issue{node.code_smells.length !== 1 ? 's' : ''}
            </span>
          )}
          
          {highComplexity && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-amber-100 text-amber-800 border border-amber-300">
              <span className="mr-1">🔄</span>
              High complexity
            </span>
          )}
          
          {node.is_entry && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-amber-100 text-amber-800 border border-amber-300">
              <span className="mr-1">🚪</span>
              Entry point
            </span>
          )}
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-xl p-6 mb-8">
        <h1 className="text-2xl font-bold flex flex-wrap items-center gap-2 mb-4">
          {node.name}
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${getNodeTypePillClass(node.type)}`}>
            {node.type}
          </span>
        </h1>
        
        {node.docstring && (
          <div className="mb-0 bg-gray-50 p-4 border-l-4 border-gray-300 rounded-r-md">
            <p className="italic text-gray-600">{node.docstring}</p>
          </div>
        )}
      </div>
      
      {renderTabs()}
      
      <div className="bg-white shadow-md rounded-xl p-6">
        {activeTab === 'overview' && (
          <div>
            {hasIssues && formatIssues(node.code_smells)}
            
            {node.metrics && (
              <div className="mb-6">
                <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-4">
                  <span className="mr-2">📊</span>
                  Summary
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {node.metrics.complexity && (
                    <div className={`p-4 rounded-lg border ${
                      node.metrics.complexity > 10 
                        ? 'bg-red-50 border-red-300' 
                        : 'bg-blue-50 border-blue-300'
                    }`}>
                      <div className="text-sm text-gray-600">Complexity</div>
                      <div className={`text-2xl font-bold ${
                        node.metrics.complexity > 10 ? 'text-red-700' : 'text-blue-700'
                      }`}>
                        {node.metrics.complexity}
                      </div>
                    </div>
                  )}
                  
                  {node.metrics.cognitive_complexity && (
                    <div className={`p-4 rounded-lg border ${
                      node.metrics.cognitive_complexity > 15 
                        ? 'bg-red-50 border-red-300' 
                        : 'bg-blue-50 border-blue-300'
                    }`}>
                      <div className="text-sm text-gray-600">Cognitive Complexity</div>
                      <div className={`text-2xl font-bold ${
                        node.metrics.cognitive_complexity > 15 ? 'text-red-700' : 'text-blue-700'
                      }`}>
                        {node.metrics.cognitive_complexity}
                      </div>
                    </div>
                  )}
                  
                  {node.metrics.lines && (
                    <div className="p-4 rounded-lg border bg-blue-50 border-blue-300">
                      <div className="text-sm text-gray-600">Lines</div>
                      <div className="text-2xl font-bold text-blue-700">
                        {node.metrics.lines}
                      </div>
                    </div>
                  )}
                  
                  <div className="p-4 rounded-lg border bg-blue-50 border-blue-300">
                    <div className="text-sm text-gray-600">Dependencies</div>
                    <div className="text-2xl font-bold text-blue-700">
                      {(connections.incoming.length + connections.outgoing.length)}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-green-600 font-semibold text-lg flex items-center mb-4">
                  <span className="mr-2">🔄</span>
                  Dependencies Overview
                </h3>
                <div className="bg-green-50 border-green-300 border p-4 rounded-md">
                  {connections.incoming.length === 0 && 
                   connections.outgoing.length === 0 ? (
                    <p className="text-gray-700">No dependencies found.</p>
                  ) : (
                    <div>
                      <div className="flex justify-between border-b pb-2 mb-2">
                        <span className="font-medium">Incoming:</span>
                        <span className="font-bold text-blue-700">{connections.incoming.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Outgoing:</span>
                        <span className="font-bold text-green-700">{connections.outgoing.length}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {node.metrics && (
                <div>
                  <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-4">
                    <span className="mr-2">📊</span>
                    Key Metrics
                  </h3>
                  <div className="bg-blue-50 border-blue-300 border p-4 rounded-md">
                    <div className="grid grid-cols-2 gap-4">
                      {node.metrics.functions && (
                        <div>
                          <div className="text-sm text-gray-600">Functions</div>
                          <div className="font-bold">{node.metrics.functions}</div>
                        </div>
                      )}
                      
                      {node.metrics.classes && (
                        <div>
                          <div className="text-sm text-gray-600">Classes</div>
                          <div className="font-bold">{node.metrics.classes}</div>
                        </div>
                      )}
                      
                      {node.metrics.params && (
                        <div>
                          <div className="text-sm text-gray-600">Parameters</div>
                          <div className="font-bold">{node.metrics.params}</div>
                        </div>
                      )}
                      
                      {node.metrics.nested_depth && (
                        <div>
                          <div className="text-sm text-gray-600">Nesting Depth</div>
                          <div className="font-bold">{node.metrics.nested_depth}</div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        {activeTab === 'project_metrics' && (
          <div>
            {loadingProjectMetrics ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-lg">Loading project metrics...</div>
              </div>
            ) : projectMetrics ? (
              <div>
                <h3 className="text-xl font-semibold mb-6">Project-Wide Metrics Dashboard</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-gray-500 text-sm font-medium">Total Files</h3>
                    <p className="text-3xl font-bold mt-2">{projectMetrics?.project_metrics?.total_files || 0}</p>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-gray-500 text-sm font-medium">Total Lines of Code</h3>
                    <p className="text-3xl font-bold mt-2">{projectMetrics?.project_metrics?.total_lines?.toLocaleString() || 0}</p>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-gray-500 text-sm font-medium">Functions</h3>
                    <p className="text-3xl font-bold mt-2">{projectMetrics?.project_metrics?.total_functions || 0}</p>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-gray-500 text-sm font-medium">Classes</h3>
                    <p className="text-3xl font-bold mt-2">{projectMetrics?.project_metrics?.total_classes || 0}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold mb-4">Quality Issues Summary</h3>
                    <div className="h-80">
                      <svg ref={donutChartRef} className="w-full"></svg>
                    </div>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold mb-4">Complexity Factors</h3>
                    <div className="h-80">
                      <svg ref={barChartRef} className="w-full"></svg>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow-md border mb-8">
                  <h3 className="text-lg font-semibold mb-4">Files with Most Issues</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="bg-gray-100">
                          <th className="py-2 px-4 text-left">File</th>
                          <th className="py-2 px-4 text-right">Lines</th>
                          <th className="py-2 px-4 text-right">Functions</th>
                          <th className="py-2 px-4 text-right">Classes</th>
                          <th className="py-2 px-4 text-right">Avg. Complexity</th>
                          <th className="py-2 px-4 text-right">Issues</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(projectMetrics.files || {})
                          .map(([filePath, fileData]: [string, any]) => {
                            const issuesCount = Object.values(fileData.issues_by_category || {})
                              .reduce((sum: number, issues: any) => sum + (issues as any[]).length, 0);
                            
                            const avgComplexity = fileData.functions && fileData.functions.length > 0
                              ? Math.round((fileData.functions.reduce((sum: number, func: any) => 
                                  sum + (func.complexity || 0), 0) / fileData.functions.length) * 10) / 10
                              : 0;
                            
                            return {
                              path: filePath,
                              name: filePath.split('/').pop(),
                              lines: fileData.lines || 0,
                              functions: fileData.functions?.length || 0,
                              classes: fileData.classes?.length || 0,
                              complexity: avgComplexity,
                              issues: issuesCount
                            };
                          })
                          .sort((a, b) => b.issues - a.issues)
                          .slice(0, 10)
                          .map((file, index) => (
                            <tr 
                              key={index} 
                              className="border-t border-gray-200 hover:bg-gray-50 cursor-pointer"
                              onClick={() => navigate(`/node/${file.path}`)}
                            >
                              <td className="py-2 px-4">{file.name}</td>
                              <td className="py-2 px-4 text-right">{file.lines}</td>
                              <td className="py-2 px-4 text-right">{file.functions}</td>
                              <td className="py-2 px-4 text-right">{file.classes}</td>
                              <td className="py-2 px-4 text-right">
                                <span className={file.complexity > 10 ? 'text-red-600 font-medium' : ''}>
                                  {file.complexity}
                                </span>
                              </td>
                              <td className="py-2 px-4 text-right">
                                <span className={`px-2 py-1 rounded-full text-white ${file.issues > 0 ? 'bg-red-500' : 'bg-green-500'}`}>
                                  {file.issues}
                                </span>
                              </td>
                            </tr>
                          ))
                        }
                      </tbody>
                    </table>
                  </div>
                </div>
                
                {issuesByCategory?.category_counts && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                    {Object.entries(issuesByCategory.category_counts).map(([category, count]) => {
                      const categoryColors: {[key: string]: string} = {
                        'security': '#ef4444',
                        'style': '#3b82f6', 
                        'duplication': '#10b981',
                        'code_smells': '#f59e0b',
                        'complexity': '#8b5cf6',
                        'sql_injection': '#ec4899'
                      };
                      
                      return (
                        <div 
                          key={category}
                          className="bg-white rounded-lg shadow-md p-6 border-t-4"
                          style={{ borderColor: categoryColors[category] || '#718096' }}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <h3 className="font-semibold text-lg mb-1">{category.replace(/_/g, ' ')}</h3>
                              <p className="text-3xl font-bold">{String(count)}</p>
                            </div>
                            <div 
                              className="p-3 rounded-full"
                              style={{ backgroundColor: `${categoryColors[category]}20` || '#71809620' }}
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: categoryColors[category] || '#718096' }}>
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                              </svg>
                            </div>
                          </div>
                          
                          <div className="mt-4 text-sm text-gray-600">
                            {category === 'security' && 'Security vulnerabilities that could compromise your application.'}
                            {category === 'style' && 'Code style issues affecting readability and maintainability.'}
                            {category === 'duplication' && 'Duplicated code blocks that should be refactored.'}
                            {category === 'code_smells' && 'Potential problems in your code structure.'}
                            {category === 'complexity' && 'Complex code that is difficult to understand and maintain.'}
                            {category === 'sql_injection' && 'SQL injection vulnerabilities requiring immediate attention.'}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center">
                <p className="text-gray-600">Failed to load project metrics. Please try again later.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'visualizations' && (
          <div>
            {renderMetricsGraphs(node)}
          </div>
        )}

        {activeTab === 'metrics' && (
          <div>
            {formatMetrics(node.metrics)}
          </div>
        )}
        
        {activeTab === 'connections' && (
          <div>
            {formatConnections(connections)}
          </div>
        )}
        
        {activeTab === 'refactoring' && (
          <div>
            {renderComplexityTimeline(node.metrics)}
          </div>
        )}
        
        {activeTab === 'impact' && (
          <div>
            {renderImpactAnalysis(nodeData)}
          </div>
        )}
        
        {activeTab === 'source' && (
          <div>
            {formatFileContent(file_content)}
          </div>
        )}
      </div>
    </div>
  );
};

export default NodeDetailsPage;