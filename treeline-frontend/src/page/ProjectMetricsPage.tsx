import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import * as d3 from 'd3';
import { 
  fetchDetailedMetrics, 
  fetchIssuesByCategory,
  fetchComplexityBreakdown,
  fetchMetricsThresholds
} from '../services/dataServices';
  
interface FunctionMetrics {
    name: string;
    line: number;
    lines: number;
    params: number;
    complexity: number;
    cognitive_complexity?: number;
    nested_depth?: number;
    returns?: number;
    code_smells: string[];
    [key: string]: any;
  }
  
  interface ClassMetrics {
    name: string;
    line: number;
    lines: number;
    methods_count?: number;
    methods?: Record<string, any>;
    complexity: number;
    code_smells: string[];
    [key: string]: any;
  }
  
  interface FileData {
    path: string;
    lines: number;
    functions: FunctionMetrics[];
    classes: ClassMetrics[];
    issues_by_category: Record<string, any[]>;
    [key: string]: any;
  }

const ProjectMetricsPage: React.FC = () => {
  const [projectMetrics, setProjectMetrics] = useState<any>(null);
  const [complexityBreakdown, setComplexityBreakdown] = useState<any>(null);
  const [issuesByCategory, setIssuesByCategory] = useState<any>(null);
  const [thresholds, setThresholds] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const donutChartRef = useRef<SVGSVGElement>(null);
  const barChartRef = useRef<SVGSVGElement>(null);
  const trendChartRef = useRef<SVGSVGElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjectData = async () => {
      try {
        setLoading(true);
        const [metricsData, complexityData, issuesData, thresholdsData] = await Promise.all([
          fetchDetailedMetrics(),
          fetchComplexityBreakdown(),
          fetchIssuesByCategory(),
          fetchMetricsThresholds()
        ]);
        
        setProjectMetrics(metricsData);
        setComplexityBreakdown(complexityData);
        setIssuesByCategory(issuesData);
        setThresholds(thresholdsData?.thresholds || {
          MAX_CYCLOMATIC_COMPLEXITY: 10,
          MAX_COGNITIVE_COMPLEXITY: 15,
          MAX_NESTED_DEPTH: 4,
          MAX_FUNCTION_LINES: 50
        });
        setError(null);
      } catch (err) {
        console.error('Error fetching project metrics:', err);
        setError('Failed to load project metrics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchProjectData();
  }, []);
  
  useEffect(() => {
    if (donutChartRef.current && issuesByCategory?.category_counts) {
      renderIssuesDonutChart();
    }
  }, [issuesByCategory, donutChartRef.current]);
  
  useEffect(() => {
    if (barChartRef.current && complexityBreakdown?.total) {
      renderComplexityBarChart();
    }
  }, [complexityBreakdown, barChartRef.current]);
  
  useEffect(() => {
    if (trendChartRef.current && projectMetrics?.files) {
      renderComplexityTrendChart();
    }
  }, [projectMetrics, trendChartRef.current]);
  
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
      'sql_injection': '#ec4899',
      'documentation': '#f472b6',
      'maintainability': '#0ea5e9',
      'file': '#64748b',
      'parsing': '#ea580c'
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

  const renderComplexityTrendChart = () => {
    if (!trendChartRef.current || !projectMetrics?.files) return;
    
    d3.select(trendChartRef.current).selectAll('*').remove();
    
    const width = 450;
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 70, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    const svg = d3.select(trendChartRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Extract complexity data from files
    const complexityData = Object.entries(projectMetrics.files).map(([_, fileData]: [string, any]) => {
      const functions = fileData.functions || [];
      
      if (functions.length === 0) return null;
      
      return functions.map((func: any) => ({
        complexity: func.complexity || 0,
        lines: func.lines || 0,
        name: func.name,
      }));
    })
    .filter(item => item !== null)
    .flat();
    
    // Group functions by complexity ranges
    const complexityRanges = [
      { min: 0, max: 5, label: '0-5' },
      { min: 6, max: 10, label: '6-10' },
      { min: 11, max: 15, label: '11-15' },
      { min: 16, max: 20, label: '16-20' },
      { min: 21, max: 1000, label: '21+' }
    ];
    
    const rangeData = complexityRanges.map(range => {
      const count = complexityData.filter(
        item => item.complexity >= range.min && item.complexity <= range.max
      ).length;
      
      return {
        label: range.label,
        count
      };
    });
    
    const x = d3.scaleBand()
      .domain(rangeData.map(d => d.label))
      .range([0, innerWidth])
      .padding(0.3);
    
    const y = d3.scaleLinear()
      .domain([0, d3.max(rangeData, d => d.count) as number])
      .range([innerHeight, 0]);
    
    svg.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x));
    
    svg.append('g')
      .call(d3.axisLeft(y));
    
    const threshold = thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10;
    
    // Add background color for high complexity ranges
    svg.selectAll('.complexity-zone')
      .data(complexityRanges)
      .enter()
      .append('rect')
      .attr('class', 'complexity-zone')
      .attr('x', d => x(d.label) as number)
      .attr('y', 0)
      .attr('width', x.bandwidth())
      .attr('height', innerHeight)
      .attr('fill', d => d.min > threshold ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)');
    
    svg.selectAll('bars')
      .data(rangeData)
      .enter()
      .append('rect')
      .attr('x', d => x(d.label) as number)
      .attr('y', d => y(d.count))
      .attr('width', x.bandwidth())
      .attr('height', d => innerHeight - y(d.count))
      .attr('fill', d => {
        const range = complexityRanges.find(r => r.label === d.label);
        return range && range.min > threshold ? '#ef4444' : '#22c55e';
      });
      
    svg.selectAll('bar-values')
      .data(rangeData)
      .enter()
      .append('text')
      .attr('x', d => (x(d.label) as number) + x.bandwidth()/2)
      .attr('y', d => y(d.count) - 5)
      .attr('text-anchor', 'middle')
      .text(d => d.count)
      .style('font-size', '12px');
    
    // Add title
    svg.append('text')
      .attr('x', innerWidth / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text('Function Complexity Distribution');

    // Add threshold line
    const thresholdX = x(complexityRanges.find(r => r.min <= threshold && r.max >= threshold)?.label as string) as number + x.bandwidth();
    svg.append('line')
      .attr('x1', thresholdX)
      .attr('y1', 0)
      .attr('x2', thresholdX)
      .attr('y2', innerHeight)
      .attr('stroke', '#ef4444')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5');
      
    svg.append('text')
      .attr('x', thresholdX + 5)
      .attr('y', 20)
      .attr('text-anchor', 'start')
      .style('font-size', '12px')
      .style('fill', '#ef4444')
      .text(`Threshold: ${threshold}`);
  };

  // Calculate project health score (0-100)
  const calculateProjectHealth = () => {
    if (!projectMetrics || !projectMetrics.project_metrics) return 0;
    
    const avgComplexity = parseFloat(projectMetrics.project_metrics.avg_complexity) || 0;
    const maxComplexity = thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10;
    
    // Factors that contribute to health score
    const complexityFactor = Math.max(0, 100 - (avgComplexity / maxComplexity) * 100);
    
    // Calculate total issues relative to codebase size
    const totalIssues = issuesByCategory?.total_issues || 0;
    const totalLines = projectMetrics.project_metrics.total_lines || 1;
    const issuesDensity = Math.min(100, (totalIssues / (totalLines / 1000)) * 10);
    const issuesFactor = Math.max(0, 100 - issuesDensity);
    
    // Weight factors and calculate final score
    const healthScore = Math.round((complexityFactor * 0.6) + (issuesFactor * 0.4));
    return Math.min(100, Math.max(0, healthScore));
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const renderHealthIndicator = () => {
    const health = calculateProjectHealth();
    return (
      <div className="flex flex-col items-center justify-center p-4">
        <div className="text-lg font-semibold mb-2">Project Health</div>
        <div className="w-32 h-32 rounded-full border-8 border-gray-200 flex items-center justify-center relative">
          <div 
            className={`absolute inset-0 rounded-full ${getHealthColor(health)}`} 
            style={{ clipPath: `polygon(50% 50%, 50% 0%, ${health > 75 ? '100% 0%, 100% 100%, ' : ''}${health > 50 ? '100% 100%, ' : ''}${health > 25 ? '0% 100%, ' : ''}0% ${health > 75 ? '100%, 50% 50%' : health > 50 ? '0%, 50% 50%' : health > 25 ? '0%, 50% 50%' : '0%, 50% 50%'})` }}
          ></div>
          <div className="text-2xl font-bold">{health}%</div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          {health >= 80 ? 'Excellent' : 
           health >= 60 ? 'Good' : 
           health >= 40 ? 'Needs Improvement' : 
           'Critical Issues'}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <div className="flex items-center space-x-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <div className="text-xl text-gray-700">Loading project metrics...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
          <div className="text-red-600 text-xl font-semibold mb-4">Error Loading Metrics</div>
          <div className="text-gray-700 mb-6">{error}</div>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-sm text-yellow-700">
              <strong>Note:</strong> Make sure your FastAPI backend is running on http://localhost:8000.
            </p>
          </div>
          <button 
            onClick={() => navigate('/')}
            className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition-colors"
          >
            Back to Visualization
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-indigo-600 text-white shadow-md">
        <div className="container mx-auto py-4 px-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Project Metrics Dashboard</h1>
            <button 
              onClick={() => navigate('/')}
              className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded transition-colors"
            >
              ← Back to Visualization
            </button>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto py-8 px-4">
        {/* Tabs */}
        <div className="mb-6 bg-white rounded-lg shadow-md overflow-hidden">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'overview' 
                  ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-500' 
                  : 'text-gray-600 hover:text-indigo-500 hover:bg-indigo-50'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('complexity')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'complexity' 
                  ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-500' 
                  : 'text-gray-600 hover:text-indigo-500 hover:bg-indigo-50'
              }`}
            >
              Complexity
            </button>
            <button
              onClick={() => setActiveTab('issues')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'issues' 
                  ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-500' 
                  : 'text-gray-600 hover:text-indigo-500 hover:bg-indigo-50'
              }`}
            >
              Issues
            </button>
            <button
              onClick={() => setActiveTab('files')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'files' 
                  ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-500' 
                  : 'text-gray-600 hover:text-indigo-500 hover:bg-indigo-50'
              }`}
            >
              Files
            </button>
          </div>
        </div>
        
        {/* Key Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col">
            <div className="text-gray-500 text-sm font-medium">Total Files</div>
            <div className="text-3xl font-bold mt-2 text-indigo-700">{projectMetrics?.project_metrics?.total_files || 0}</div>
            <div className="text-sm text-gray-500 mt-2">Python source files</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col">
            <div className="text-gray-500 text-sm font-medium">Lines of Code</div>
            <div className="text-3xl font-bold mt-2 text-indigo-700">{projectMetrics?.project_metrics?.total_lines?.toLocaleString() || 0}</div>
            <div className="text-sm text-gray-500 mt-2">Total source lines</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col">
            <div className="text-gray-500 text-sm font-medium">Functions</div>
            <div className="text-3xl font-bold mt-2 text-indigo-700">{projectMetrics?.project_metrics?.total_functions || 0}</div>
            <div className="text-sm text-gray-500 mt-2">Total functions/methods</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col">
            <div className="text-gray-500 text-sm font-medium">Classes</div>
            <div className="text-3xl font-bold mt-2 text-indigo-700">{projectMetrics?.project_metrics?.total_classes || 0}</div>
            <div className="text-sm text-gray-500 mt-2">Total classes</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col">
            <div className="text-gray-500 text-sm font-medium">Issues</div>
            <div className="text-3xl font-bold mt-2 text-red-600">{issuesByCategory?.total_issues || 0}</div>
            <div className="text-sm text-gray-500 mt-2">Total quality issues</div>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Project Overview</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-700 mb-3">Key Metrics</h3>
                    <table className="w-full">
                      <tbody>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Average Complexity</td>
                          <td className="py-2 font-medium text-right">
                            <span className={parseFloat(projectMetrics?.project_metrics?.avg_complexity) > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) ? 'text-red-600' : 'text-green-600'}>
                              {projectMetrics?.project_metrics?.avg_complexity || 0}
                            </span>
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Max Complexity</td>
                          <td className="py-2 font-medium text-right">
                            <span className="text-amber-600">
                              {projectMetrics?.project_metrics?.max_complexity || 0}
                            </span>
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Complex Functions</td>
                          <td className="py-2 font-medium text-right">
                            <span className={projectMetrics?.project_metrics?.complex_functions_count > 0 ? 'text-amber-600' : 'text-green-600'}>
                              {projectMetrics?.project_metrics?.complex_functions_count || 0}
                            </span>
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Total Issues</td>
                          <td className="py-2 font-medium text-right">
                            <span className={issuesByCategory?.total_issues > 0 ? 'text-red-600' : 'text-green-600'}>
                              {issuesByCategory?.total_issues || 0}
                            </span>
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Entry Points</td>
                          <td className="py-2 font-medium text-right">
                            {projectMetrics?.dependency_metrics?.entry_points || 0}
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 text-gray-700">Avg Dependencies</td>
                          <td className="py-2 font-medium text-right">
                            {projectMetrics?.dependency_metrics?.avg_dependencies || 0}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-700 mb-3">Quality Thresholds</h3>
                    <table className="w-full">
                      <tbody>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Max Cyclomatic Complexity</td>
                          <td className="py-2 font-medium text-right">
                            {thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10}
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Max Cognitive Complexity</td>
                          <td className="py-2 font-medium text-right">
                            {thresholds?.MAX_COGNITIVE_COMPLEXITY || 15}
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Max Function Lines</td>
                          <td className="py-2 font-medium text-right">
                            {thresholds?.MAX_FUNCTION_LINES || 50}
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Max Nested Depth</td>
                          <td className="py-2 font-medium text-right">
                            {thresholds?.MAX_NESTED_DEPTH || 4}
                          </td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-2 text-gray-700">Max Parameters</td>
                          <td className="py-2 font-medium text-right">
                            {thresholds?.MAX_PARAMS || 5}
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 text-gray-700">Max Returns</td>
                          <td className="py-2 font-medium text-right">
                            {thresholds?.MAX_RETURNS || 4}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-700 mb-3">Project Summary</h3>
                  <div className="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-r-md">
                    <p className="text-gray-700 mb-2">
                      This project contains <span className="font-medium">{projectMetrics?.project_metrics?.total_files || 0} files</span> with 
                      <span className="font-medium"> {projectMetrics?.project_metrics?.total_functions || 0} functions</span> and 
                      <span className="font-medium"> {projectMetrics?.project_metrics?.total_classes || 0} classes</span>.
                    </p>
                    <p className="text-gray-700 mb-2">
                      The average cyclomatic complexity is <span className={`font-medium ${parseFloat(projectMetrics?.project_metrics?.avg_complexity) > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) ? 'text-red-600' : 'text-green-600'}`}>
                        {projectMetrics?.project_metrics?.avg_complexity || 0}
                      </span> and there are <span className="font-medium">{projectMetrics?.project_metrics?.complex_functions_count || 0}</span> complex functions.
                    </p>
                    <p className="text-gray-700">
                      There are <span className={`font-medium ${issuesByCategory?.total_issues > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {issuesByCategory?.total_issues || 0} code quality issues
                      </span> identified in the codebase.
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Complexity Distribution Chart */}
              <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                <h3 className="text-lg font-medium text-gray-700 mb-3">Function Complexity Distribution</h3>
                <div className="h-80">
                  <svg ref={trendChartRef} className="w-full h-full"></svg>
                </div>
              </div>
            </div>
            
            <div>
              {/* Project Health Status */}
              <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                {renderHealthIndicator()}
              </div>
              
              {/* Most Complex Files */}
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-medium text-gray-700 mb-3">Most Complex Files</h3>
                <div className="overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
                        <th className="py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Complexity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(projectMetrics?.files || {})
                        .map(([filePath, fileData]: [string, any]) => {
                          // Calculate average complexity for the file
                          const totalComplexity = fileData.functions?.reduce((sum: number, func: any) => 
                            sum + (func.complexity || 0), 0) || 0;
                          const avgComplexity = fileData.functions?.length > 0 
                            ? totalComplexity / fileData.functions.length
                            : 0;
                          
                          return {
                            path: filePath,
                            name: filePath.split('/').pop(),
                            complexity: avgComplexity
                          };
                        })
                        .sort((a, b) => b.complexity - a.complexity)
                        .slice(0, 5)
                        .map((file, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="py-2">
                              <span className="text-sm text-gray-900 truncate block max-w-xs">
                                {file.name}
                              </span>
                            </td>
                            <td className="py-2 text-right">
                              <span className={`text-sm font-medium ${file.complexity > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) ? 'text-red-600' : 'text-green-600'}`}>
                                {file.complexity.toFixed(1)}
                              </span>
                            </td>
                          </tr>
                        ))
                      }
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'complexity' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Complexity Factors */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Complexity Factors</h3>
              <div className="h-80">
                <svg ref={barChartRef} className="w-full h-full"></svg>
              </div>
            </div>
            
            {/* Complexity Metrics */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Complexity Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4">
                  <div className="text-sm text-gray-500">Average Complexity</div>
                  <div className="text-2xl font-bold mt-1">
                    <span className={parseFloat(projectMetrics?.project_metrics?.avg_complexity) > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) ? 'text-red-600' : 'text-green-600'}>
                      {projectMetrics?.project_metrics?.avg_complexity || 0}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Threshold: {thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10}
                  </div>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="text-sm text-gray-500">Maximum Complexity</div>
                  <div className="text-2xl font-bold mt-1">
                    <span className="text-amber-600">
                      {projectMetrics?.project_metrics?.max_complexity || 0}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {projectMetrics?.project_metrics?.max_complexity > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) 
                      ? 'Exceeds threshold' 
                      : 'Within threshold'}
                  </div>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="text-sm text-gray-500">Complex Functions</div>
                  <div className="text-2xl font-bold mt-1">
                    <span className={projectMetrics?.project_metrics?.complex_functions_count > 0 ? 'text-amber-600' : 'text-green-600'}>
                      {projectMetrics?.project_metrics?.complex_functions_count || 0}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Complexity {thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10}
                  </div>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="text-sm text-gray-500">Code Health Score</div>
                  <div className="text-2xl font-bold mt-1">
                    <span className="text-indigo-600">
                      {calculateProjectHealth()}%
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Based on complexity & issues
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <h4 className="font-medium text-gray-700 mb-2">Most Complex Functions</h4>
                <div className="overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Function</th>
                        <th className="py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Lines</th>
                        <th className="py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Complexity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(projectMetrics?.files || {})
                        .flatMap(([filePath, fileData]: [string, any]) => 
                          (fileData.functions || []).map((func: any) => ({
                            name: func.name,
                            file: filePath.split('/').pop(),
                            lines: func.lines || 0,
                            complexity: func.complexity || 0
                          }))
                        )
                        .sort((a, b) => b.complexity - a.complexity)
                        .slice(0, 10)
                        .map((func, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="py-2">
                              <div className="text-sm font-medium text-gray-900">{func.name}</div>
                              <div className="text-xs text-gray-500">{func.file}</div>
                            </td>
                            <td className="py-2 text-right text-sm text-gray-500">
                              {func.lines}
                            </td>
                            <td className="py-2 text-right">
                              <span className={`text-sm font-medium ${func.complexity > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) ? 'text-red-600' : 'text-green-600'}`}>
                                {func.complexity}
                              </span>
                            </td>
                          </tr>
                        ))
                      }
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            
            {/* Complexity Distribution */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Complexity Distribution</h3>
              <div className="h-80">
                <svg ref={trendChartRef} className="w-full h-full"></svg>
              </div>
            </div>
            
            {/* Complexity Thresholds */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Complexity Thresholds & Guidelines</h3>
              <div className="space-y-4">
                <div className="p-4 bg-indigo-50 rounded-lg">
                  <h4 className="font-medium text-indigo-700 mb-1">Cyclomatic Complexity</h4>
                  <p className="text-sm text-gray-700">
                    Measures the number of independent paths through a program. Keep functions below 
                    <span className="font-bold"> {thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10}</span> for good maintainability.
                  </p>
                </div>
                
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-700 mb-1">Cognitive Complexity</h4>
                  <p className="text-sm text-gray-700">
                    Measures how difficult code is to understand. Functions should aim to stay under 
                    <span className="font-bold"> {thresholds?.MAX_COGNITIVE_COMPLEXITY || 15}</span>.
                  </p>
                </div>
                
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-700 mb-1">Nesting Depth</h4>
                  <p className="text-sm text-gray-700">
                    Deeply nested code is harder to understand. Keep nesting below 
                    <span className="font-bold"> {thresholds?.MAX_NESTED_DEPTH || 4}</span> levels.
                  </p>
                </div>
                
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h4 className="font-medium text-purple-700 mb-1">Function Size</h4>
                  <p className="text-sm text-gray-700">
                    Functions should ideally be limited to 
                    <span className="font-bold"> {thresholds?.MAX_FUNCTION_LINES || 50}</span> lines or less.
                    Longer functions tend to have multiple responsibilities.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'issues' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Issues Overview */}
            <div className="lg:col-span-2">
              <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                <h3 className="text-lg font-medium text-gray-700 mb-4">Quality Issues Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="h-80">
                    <svg ref={donutChartRef} className="w-full h-full"></svg>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Issue Distribution</h4>
                    <div className="space-y-3">
                      {Object.entries(issuesByCategory?.category_counts || {})
                        .sort(([, a], [, b]) => (b as number) - (a as number))
                        .map(([category, count]) => {
                            const countValue = count as number;
                          const categoryColors: {[key: string]: string} = {
                            'security': '#ef4444',
                            'style': '#3b82f6', 
                            'duplication': '#10b981',
                            'code_smells': '#f59e0b',
                            'complexity': '#8b5cf6',
                            'sql_injection': '#ec4899',
                            'documentation': '#f472b6',
                            'maintainability': '#0ea5e9',
                            'file': '#64748b',
                            'parsing': '#ea580c'
                          };
                          
                          const totalIssues = Object.values(issuesByCategory?.category_counts || {})
                            .reduce((sum: number, value: any) => sum + value, 0);
                          const percentage = totalIssues > 0 
                            ? Math.round((count as number) / totalIssues * 100) 
                            : 0;
                          
                          return (
                            <div key={category}>
                              <div className="flex justify-between mb-1">
                                <span className="text-sm font-medium text-gray-700">
                                  {category.replace(/_/g, ' ')}
                                </span>
                                <span className="text-sm text-gray-500">
                                  {countValue} ({percentage}%)
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="h-2 rounded-full" 
                                  style={{ 
                                    width: `${percentage}%`,
                                    backgroundColor: categoryColors[category] || '#6b7280'
                                  }}
                                ></div>
                              </div>
                            </div>
                          );
                        })
                      }
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-medium text-gray-700 mb-4">Files with Most Issues</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="py-3 px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
                        <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Lines</th>
                        <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Functions</th>
                        <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Classes</th>
                        <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Avg. Complexity</th>
                        <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Issues</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {Object.entries(projectMetrics?.files || {})
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
                            className="hover:bg-gray-50 cursor-pointer"
                            onClick={() => navigate(`/files/${encodeURIComponent(file.path)}`)}
                          >
                            <td className="py-3 px-6 text-sm">
                              <div className="font-medium text-gray-900">{file.name}</div>
                              <div className="text-gray-500 text-xs truncate max-w-xs">{file.path}</div>
                            </td>
                            <td className="py-3 px-3 text-center text-sm text-gray-500">{file.lines}</td>
                            <td className="py-3 px-3 text-center text-sm text-gray-500">{file.functions}</td>
                            <td className="py-3 px-3 text-center text-sm text-gray-500">{file.classes}</td>
                            <td className="py-3 px-3 text-center">
                              <span className={`text-sm font-medium ${file.complexity > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) ? 'text-red-600' : 'text-green-600'}`}>
                                {file.complexity}
                              </span>
                            </td>
                            <td className="py-3 px-3 text-center">
                              <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                file.issues > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                              }`}>
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
            </div>
            
            {/* Issue Categories */}
            <div>
              <div className="grid grid-cols-1 gap-4">
                {issuesByCategory?.category_counts && Object.entries(issuesByCategory.category_counts)
                  .sort(([, a], [, b]) => (b as number) - (a as number))
                  .map(([category, count]) => {
                    const categoryColors: {[key: string]: string} = {
                      'security': '#ef4444',
                      'style': '#3b82f6', 
                      'duplication': '#10b981',
                      'code_smells': '#f59e0b',
                      'complexity': '#8b5cf6',
                      'sql_injection': '#ec4899',
                      'documentation': '#f472b6',
                      'maintainability': '#0ea5e9',
                      'file': '#64748b',
                      'parsing': '#ea580c'
                    };

                    const descriptions: {[key: string]: string} = {
                      'security': 'Security vulnerabilities that could compromise your application.',
                      'style': 'Code style issues affecting readability and maintainability.',
                      'duplication': 'Duplicated code blocks that should be refactored.',
                      'code_smells': 'Potential problems in your code structure.',
                      'complexity': 'Complex code that is difficult to understand and maintain.',
                      'sql_injection': 'SQL injection vulnerabilities requiring immediate attention.',
                      'documentation': 'Missing or inadequate documentation.',
                      'maintainability': 'Issues that make the code harder to maintain over time.',
                      'file': 'Problems related to file structure or I/O operations.',
                      'parsing': 'Syntax or parsing errors in the code.'
                    };
                    
                    return (
                      <div 
                        key={category}
                        className="bg-white rounded-lg shadow-md p-4 border-t-4"
                        style={{ borderColor: categoryColors[category] || '#718096' }}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-semibold text-lg mb-1">{category.replace(/_/g, ' ')}</h3>
                            <p className="text-2xl font-bold">{String(count)}</p>
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
                        
                        <div className="mt-3 text-sm text-gray-600">
                          {descriptions[category] || 'Issues affecting code quality.'}
                        </div>
                      </div>
                    );
                  })
                }
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'files' && (
          <div className="grid grid-cols-1 gap-6">
            {/* Files Table */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-700 mb-4">All Files</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="py-3 px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
                      <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Lines</th>
                      <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Functions</th>
                      <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Classes</th>
                      <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Complexity</th>
                      <th className="py-3 px-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Issues</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(projectMetrics?.files || {})
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
                      .sort((a, b) => (a.name && b.name) ? a.name.localeCompare(b.name) : 0)
                      .map((file, index) => (
                        <tr 
                          key={index} 
                          className="hover:bg-gray-50 cursor-pointer"
                          onClick={() => navigate(`/files/${encodeURIComponent(file.path)}`)}
                        >
                          <td className="py-3 px-6 text-sm">
                            <div className="font-medium text-gray-900">{file.name}</div>
                            <div className="text-gray-500 text-xs truncate max-w-xs">{file.path}</div>
                          </td>
                          <td className="py-3 px-3 text-center text-sm text-gray-500">{file.lines}</td>
                          <td className="py-3 px-3 text-center text-sm text-gray-500">{file.functions}</td>
                          <td className="py-3 px-3 text-center text-sm text-gray-500">{file.classes}</td>
                          <td className="py-3 px-3 text-center">
                            <span className={`text-sm font-medium ${file.complexity > (thresholds?.MAX_CYCLOMATIC_COMPLEXITY || 10) ? 'text-red-600' : 'text-green-600'}`}>
                              {file.complexity}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-center">
                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              file.issues > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                            }`}>
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
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-medium text-gray-700 mb-4">Files by Size</h3>
                <div className="space-y-4">
                  {['Large Files (> 500 lines)', 'Medium Files (100-500 lines)', 'Small Files (< 100 lines)'].map((category, index) => {
                    const largeFiles = (Object.values(projectMetrics?.files || {}) as FileData[]).filter(file => file.lines > 500).length;
                    const mediumFiles = (Object.values(projectMetrics?.files || {}) as FileData[]).filter(file => file.lines >= 100 && file.lines <= 500).length;
                    const smallFiles = (Object.values(projectMetrics?.files || {}) as FileData[]).filter(file => file.lines < 100).length;
                    const totalFiles = largeFiles + mediumFiles + smallFiles;
                    
                    const counts = [largeFiles, mediumFiles, smallFiles];
                    const percentages = totalFiles > 0 ? [
                      Math.round(largeFiles / totalFiles * 100),
                      Math.round(mediumFiles / totalFiles * 100),
                      Math.round(smallFiles / totalFiles * 100)
                    ] : [0, 0, 0];
                    
                    const colors = ['#ef4444', '#f59e0b', '#22c55e'];
                    
                    return (
                      <div key={index}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">{category}</span>
                          <span className="text-sm text-gray-500">
                            {counts[index]} ({percentages[index]}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="h-2 rounded-full" 
                            style={{ 
                              width: `${percentages[index]}%`,
                              backgroundColor: colors[index]
                            }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                  
                  <div className="pt-4 border-t mt-6">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Average File Size:</span>
                      <span>
                        {Math.round(projectMetrics?.project_metrics?.total_lines / 
                                  (projectMetrics?.project_metrics?.total_files || 1))} lines
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Largest File:</span>
                      <span>
                      {Math.max(...(Object.values(projectMetrics?.files || {}) as FileData[])
                        .map(file => file.lines || 0))} lines
                      </span>
                    </div>
                  </div>
                </div>
              </div>
                </div>
              </div>
        )}
      </main>
    </div>
  );
};

export default ProjectMetricsPage;