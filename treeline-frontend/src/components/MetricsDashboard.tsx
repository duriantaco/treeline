import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import * as d3 from 'd3';
import { 
  fetchDetailedMetrics,
  fetchFileDetailedMetrics,
  fetchComplexityBreakdown,
  fetchIssuesByCategory 
} from '../services/dataServices';
import ComplexityTimeline from './ComplexityTimeline';
import ImpactAnalysis from './ImpactAnalysis';
import {
  MetricsData,
  FileMetricsData,
  ComplexityBreakdownData,
  IssuesByCategoryData,
  FileInfo,
  PreparedFileMetric
} from '../types/metrics';

const MetricsDashboardPage: React.FC = () => {
  const [data, setData] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [fileMetrics, setFileMetrics] = useState<FileMetricsData | null>(null);
  const [complexityBreakdown, setComplexityBreakdown] = useState<ComplexityBreakdownData | null>(null);
  const [issuesByCategory, setIssuesByCategory] = useState<IssuesByCategoryData | null>(null);
  
  const donutChartRef = useRef<SVGSVGElement>(null);
  const barChartRef = useRef<SVGSVGElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAllMetricsData = async () => {
      try {
        setLoading(true);
        
        // Fetch all metrics in parallel
        const [metricsData, complexityData, issuesData] = await Promise.all([
          fetchDetailedMetrics(),
          fetchComplexityBreakdown(),
          fetchIssuesByCategory()
        ]);
        
        setData(metricsData as MetricsData);
        setComplexityBreakdown(complexityData as ComplexityBreakdownData);
        setIssuesByCategory(issuesData as IssuesByCategoryData);
        
        // Set first file as active if available
        if (metricsData.files && Object.keys(metricsData.files).length > 0) {
          const firstFilePath = Object.keys(metricsData.files)[0];
          setActiveFile(firstFilePath);
          const fileData = await fetchFileDetailedMetrics(firstFilePath);
          setFileMetrics(fileData as FileMetricsData);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching metrics data:', err);
        setError('Failed to load metrics data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAllMetricsData();
  }, []);
  
  useEffect(() => {
    if (donutChartRef.current && data && issuesByCategory) {
      renderIssuesDonutChart();
    }
  }, [data, issuesByCategory, donutChartRef.current]);
  
  useEffect(() => {
    if (barChartRef.current && complexityBreakdown) {
      renderComplexityBarChart();
    }
  }, [complexityBreakdown, barChartRef.current]);
  
  const fetchFileData = async (filePath: string) => {
    try {
      setActiveFile(filePath);
      const fileData = await fetchFileDetailedMetrics(filePath);
      setFileMetrics(fileData as FileMetricsData);
    } catch (err) {
      console.error(`Error fetching data for file ${filePath}:`, err);
    }
  };
  
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
  
  const prepareFileMetricsData = (): PreparedFileMetric[] => {
    if (!data?.files) return [];
    
    return Object.entries(data.files)
      .map(([filePath, fileData]) => {
        const fileInfo = fileData as FileInfo;
        const issuesCount = Object.values(fileInfo.issues_by_category || {})
          .reduce((sum: number, issues: any) => sum + (issues as any[]).length, 0);
        
        return {
          name: filePath.split('/').pop() || '',
          path: filePath,
          lines: fileInfo.lines || 0,
          functions: fileInfo.functions?.length || 0,
          classes: fileInfo.classes?.length || 0,
          issues: issuesCount,
          complexity: calculateAverageComplexity(fileInfo)
        };
      })
      .sort((a, b) => b.issues - a.issues);
  };
  
  const calculateAverageComplexity = (fileData: FileInfo): number => {
    if (!fileData.functions || fileData.functions.length === 0) return 0;
    
    const totalComplexity = fileData.functions.reduce((sum: number, func) => 
      sum + (func.complexity || 0), 0);
    
    return Math.round((totalComplexity / fileData.functions.length) * 10) / 10;
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading metrics data...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center h-screen flex-col">
        <div className="text-xl text-red-600 mb-4">Error loading metrics</div>
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
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Code Quality Dashboard</h1>
        <button 
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Back to Visualization
        </button>
      </div>
      
      {/* Navigation Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex space-x-4">
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'overview' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'files' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('files')}
          >
            Files Analysis
          </button>
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'issues' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('issues')}
          >
            Quality Issues
          </button>
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'complexity' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('complexity')}
          >
            Complexity Analysis
          </button>
        </div>
      </div>
      
      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-gray-500 text-sm font-medium">Total Files</h3>
              <p className="text-3xl font-bold mt-2">{data?.project_metrics?.total_files || 0}</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-gray-500 text-sm font-medium">Total Lines of Code</h3>
              <p className="text-3xl font-bold mt-2">{data?.project_metrics?.total_lines?.toLocaleString() || 0}</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-gray-500 text-sm font-medium">Functions</h3>
              <p className="text-3xl font-bold mt-2">{data?.project_metrics?.total_functions || 0}</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-gray-500 text-sm font-medium">Classes</h3>
              <p className="text-3xl font-bold mt-2">{data?.project_metrics?.total_classes || 0}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">Quality Issues Summary</h3>
              <div className="h-80">
                <svg ref={donutChartRef} className="w-full"></svg>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">Complexity Factors</h3>
              <div className="h-80">
                <svg ref={barChartRef} className="w-full"></svg>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
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
                    {prepareFileMetricsData().slice(0, 10).map((file, index) => (
                      <tr 
                        key={index} 
                        className={`border-t border-gray-200 hover:bg-gray-50 cursor-pointer ${file.path === activeFile ? 'bg-blue-50' : ''}`}
                        onClick={() => fetchFileData(file.path)}
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
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Files Analysis Tab */}
      {activeTab === 'files' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow-md h-[calc(100vh-200px)] overflow-auto">
            <h3 className="text-lg font-semibold mb-4">Files</h3>
            <div className="space-y-2">
              {prepareFileMetricsData().map((file, index) => (
                <div 
                  key={index}
                  className={`p-3 rounded-md cursor-pointer flex justify-between items-center ${file.path === activeFile ? 'bg-blue-100' : 'hover:bg-gray-100'}`}
                  onClick={() => fetchFileData(file.path)}
                >
                  <div className="flex items-center">
                    <div className="mr-3">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0v12h8V4H6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-sm truncate" style={{maxWidth: '200px'}}>{file.name}</div>
                      <div className="text-xs text-gray-500">{file.lines} lines</div>
                    </div>
                  </div>
                  {file.issues > 0 && (
                    <span className="px-2 py-1 text-xs rounded-full bg-red-500 text-white">{file.issues}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md h-[calc(100vh-200px)] overflow-auto">
            {fileMetrics ? (
              <div>
                <h3 className="text-xl font-semibold mb-4">{fileMetrics.path.split('/').pop()}</h3>
                <div className="mb-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-gray-100 p-4 rounded-md">
                      <div className="text-sm text-gray-500">Lines</div>
                      <div className="text-2xl font-semibold">{fileMetrics.lines}</div>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-md">
                      <div className="text-sm text-gray-500">Functions</div>
                      <div className="text-2xl font-semibold">{fileMetrics.functions?.length || 0}</div>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-md">
                      <div className="text-sm text-gray-500">Classes</div>
                      <div className="text-2xl font-semibold">{fileMetrics.classes?.length || 0}</div>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-md">
                      <div className="text-sm text-gray-500">Issues</div>
                      <div className="text-2xl font-semibold">
                        {Object.values(fileMetrics.issues_by_category || {}).reduce((sum: number, issues: any[]) => sum + issues.length, 0)}
                      </div>
                    </div>
                  </div>
                  
                  {/* Issues by category */}
                  {Object.keys(fileMetrics.issues_by_category || {}).length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold mb-2">Issues</h4>
                      <div className="space-y-4">
                        {Object.entries(fileMetrics.issues_by_category).map(([category, issues]) => (
                          <div key={category} className="border-l-4 p-4" 
                               style={{borderColor: 
                                 category === 'security' ? '#ef4444' :
                                 category === 'style' ? '#3b82f6' :
                                 category === 'duplication' ? '#10b981' :
                                 category === 'code_smells' ? '#f59e0b' :
                                 category === 'complexity' ? '#8b5cf6' :
                                 category === 'sql_injection' ? '#ec4899' : '#718096'
                               }}>
                            <h5 className="font-medium mb-2">{category.replace(/_/g, ' ')} ({issues.length})</h5>
                            <ul className="space-y-1 text-sm">
                              {issues.slice(0, 5).map((issue, i) => (
                                <li key={i} className="flex justify-between">
                                  <span>{issue.description}</span>
                                  {issue.line && <span className="text-gray-500">Line {issue.line}</span>}
                                </li>
                              ))}
                              {issues.length > 5 && (
                                <li className="text-gray-500 italic">...and {issues.length - 5} more</li>
                              )}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Functions with complexity */}
                  {fileMetrics.functions && fileMetrics.functions.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold mb-2">Functions</h4>
                      <table className="min-w-full">
                        <thead>
                          <tr className="bg-gray-100">
                            <th className="py-2 px-4 text-left">Name</th>
                            <th className="py-2 px-4 text-right">Lines</th>
                            <th className="py-2 px-4 text-right">Params</th>
                            <th className="py-2 px-4 text-right">Complexity</th>
                            <th className="py-2 px-4 text-right">Cognitive</th>
                            <th className="py-2 px-4 text-right">Nested Depth</th>
                            <th className="py-2 px-4 text-right">Issues</th>
                          </tr>
                        </thead>
                        <tbody>
                          {fileMetrics.functions.slice().sort((a, b) => (b.complexity || 0) - (a.complexity || 0)).map((func, index) => (
                            <tr key={index} className="border-t border-gray-200 hover:bg-gray-50">
                              <td className="py-2 px-4">{func.name}</td>
                              <td className="py-2 px-4 text-right">{func.lines}</td>
                              <td className="py-2 px-4 text-right">{func.params}</td>
                              <td className="py-2 px-4 text-right">
                                <span className={func.complexity !== undefined && func.complexity > 10 ? 'text-red-600 font-medium' : ''}>
                                  {func.complexity !== undefined ? func.complexity : 'N/A'}
                                </span>
                              </td>
                              <td className="py-2 px-4 text-right">
                                <span className={func.cognitive_complexity !== undefined && func.cognitive_complexity > 15 ? 'text-red-600 font-medium' : ''}>
                                  {func.cognitive_complexity !== undefined ? func.cognitive_complexity : 'N/A'}
                                </span>
                              </td>
                              <td className="py-2 px-4 text-right">
                                <span className={func.nested_depth !== undefined && func.nested_depth > 4 ? 'text-red-600 font-medium' : ''}>
                                  {func.nested_depth !== undefined ? func.nested_depth : 'N/A'}
                                </span>
                              </td>
                              <td className="py-2 px-4 text-right">
                                <span className="px-2 py-1 rounded-full text-white bg-gray-500">
                                  {func.code_smells?.length || 0}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-lg text-gray-500">Select a file to view detailed metrics</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Quality Issues Tab */}
      {activeTab === 'issues' && (
        <div className="grid grid-cols-1 gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {issuesByCategory?.category_counts && Object.entries(issuesByCategory.category_counts).map(([category, count]) => {
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
                      <p className="text-3xl font-bold">{count as number}</p>
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
          
          {issuesByCategory?.files_with_most_issues && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">Files with Most Issues</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="py-2 px-4 text-left">File</th>
                      <th className="py-2 px-4 text-right">Total Issues</th>
                      {Object.keys({
                        'security': '#ef4444',
                        'style': '#3b82f6', 
                        'duplication': '#10b981',
                        'code_smells': '#f59e0b',
                        'complexity': '#8b5cf6',
                        'sql_injection': '#ec4899'
                      }).map(category => (
                        <th key={category} className="py-2 px-4 text-right">{category.replace(/_/g, ' ')}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {issuesByCategory.files_with_most_issues.map((file, index) => (
                      <tr 
                        key={index} 
                        className="border-t border-gray-200 hover:bg-gray-50 cursor-pointer"
                        onClick={() => fetchFileData(file.file_path)}
                      >
                        <td className="py-2 px-4">{file.file_path.split('/').pop()}</td>
                        <td className="py-2 px-4 text-right font-medium">{file.issue_count}</td>
                        {Object.keys({
                          'security': '#ef4444',
                          'style': '#3b82f6', 
                          'duplication': '#10b981',
                          'code_smells': '#f59e0b',
                          'complexity': '#8b5cf6',
                          'sql_injection': '#ec4899'
                        }).map(category => (
                          <td key={category} className="py-2 px-4 text-right">
                            {file[category] ? (
                              <span className="px-2 py-1 rounded-full text-white" 
                                    style={{backgroundColor: 
                                      category === 'security' ? '#ef4444' :
                                      category === 'style' ? '#3b82f6' :
                                      category === 'duplication' ? '#10b981' :
                                      category === 'code_smells' ? '#f59e0b' :
                                      category === 'complexity' ? '#8b5cf6' :
                                      category === 'sql_injection' ? '#ec4899' : '#718096'
                                    }}>
                                {file[category]}
                              </span>
                            ) : '0'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Complexity Analysis Tab */}
      {activeTab === 'complexity' && (
        <div className="grid grid-cols-1 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Complexity Distribution</h3>
            <div className="h-80 mb-6">
              <svg ref={barChartRef} className="w-full"></svg>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <div className="border rounded-lg p-5">
                <h4 className="font-medium mb-2">Cyclomatic Complexity</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Measures the number of linearly independent paths through a program's source code.
                  High complexity may indicate difficult-to-test code.
                </p>
                <div className="flex items-center justify-between">
                  <div>Avg: <span className="font-bold">{data?.project_metrics?.avg_complexity || 'N/A'}</span></div>
                  <div>Max: <span className="font-bold">{data?.project_metrics?.max_complexity || 'N/A'}</span></div>
                </div>
              </div>
              
              <div className="border rounded-lg p-5">
                <h4 className="font-medium mb-2">Cognitive Complexity</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Measures how difficult code is to understand. Accounts for nesting, control flow 
                  structures and other cognitive load factors.
                </p>
                <div className="flex items-center justify-between">
                  <div>Threshold: <span className="font-bold">15</span></div>
                  <div>Complex Functions: <span className="font-bold">{
                    complexityBreakdown?.total?.high_cognitive_complexity || 'N/A'
                  }</span></div>
                </div>
              </div>
              
              <div className="border rounded-lg p-5">
                <h4 className="font-medium mb-2">Nesting Depth</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Measures how deeply nested control structures are in your code.
                  Deep nesting makes code harder to understand.
                </p>
                <div className="flex items-center justify-between">
                  <div>Threshold: <span className="font-bold">4</span></div>
                  <div>Deeply Nested: <span className="font-bold">{
                    complexityBreakdown?.total?.high_nesting || 'N/A'
                  }</span></div>
                </div>
              </div>
            </div>
          </div>
          
          {fileMetrics && fileMetrics.functions && fileMetrics.functions.length > 0 && fileMetrics.functions.some((f) => (f.complexity || 0) > 0) && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">Complexity Refactoring Projection</h3>
              <p className="text-sm text-gray-600 mb-4">
                This chart shows how refactoring could reduce complexity metrics for the selected file's function with highest complexity.
              </p>
              
              {/* Find the function with highest complexity */}
              {(() => {
                // Safe to use because we already checked above that fileMetrics and functions exist and have length > 0
                const mostComplexFunction = [...(fileMetrics.functions || [])].sort((a, b) => 
                  (b.complexity || 0) - (a.complexity || 0)
                )[0];
                
                if (mostComplexFunction) {
                  return (
                    <div>
                      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                        <h4 className="font-medium">{mostComplexFunction.name}</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                          <div>
                            <div className="text-xs text-gray-500">Complexity</div>
                            <div className="text-lg font-semibold">{mostComplexFunction.complexity || 0}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Cognitive</div>
                            <div className="text-lg font-semibold">{mostComplexFunction.cognitive_complexity || 0}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Nesting</div>
                            <div className="text-lg font-semibold">{mostComplexFunction.nested_depth || 0}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Issues</div>
                            <div className="text-lg font-semibold">{mostComplexFunction.code_smells?.length || 0}</div>
                          </div>
                        </div>
                      </div>
                      
                      <ComplexityTimeline 
                        currentComplexity={mostComplexFunction.complexity || 0}
                        currentCognitiveComplexity={mostComplexFunction.cognitive_complexity || 0}
                        currentNestedDepth={mostComplexFunction.nested_depth || 0}
                      />
                    </div>
                  );
                }
                
                return (
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <p>No complexity data available for functions in this file.</p>
                  </div>
                );
              })()}
            </div>
          )}
          
          {activeFile && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">Impact Analysis</h3>
              <p className="text-sm text-gray-600 mb-4">
                This shows how changes to the selected file might impact other parts of the codebase.
              </p>
              
              {fileMetrics ? (
                <ImpactAnalysis 
                  nodeId={activeFile}
                  nodeName={activeFile.split('/').pop() || ''}
                  nodeType="file"
                  connections={{
                    incoming: [],  
                    outgoing: []   
                  }}
                  hasIssues={Object.values(fileMetrics.issues_by_category || {}).some((issues) => issues.length > 0)}
                  highComplexity={fileMetrics.functions && fileMetrics.functions.some((f) => (f.complexity || 0) > 10) || false}
                />
              ) : (
                <div className="p-4 bg-gray-50 rounded-lg text-center">
                  <p>Select a file to view impact analysis.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MetricsDashboardPage;