import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import * as d3 from 'd3';
import { 
  fetchDetailedMetrics, 
  fetchIssuesByCategory, 
  fetchComplexityBreakdown,
} from '../services/dataServices';
import { FileTableItem, FileData, ViewOption, ComplexFunction } from '../types/metrics';

const ProjectMetricsPage: React.FC = () => {
  const [projectMetrics, setProjectMetrics] = useState<any | null>(null);
  const [complexityBreakdown, setComplexityBreakdown] = useState<any>(null);
  const [issuesByCategory, setIssuesByCategory] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filesList, setFilesList] = useState<FileTableItem[]>([]);
  const [viewMode, setViewMode] = useState<number | null>(10);
  const donutChartRef = useRef<SVGSVGElement>(null);
  const barChartRef = useRef<SVGSVGElement>(null);

  const navigate = useNavigate();

  const viewOptions: ViewOption[] = [
    { label: 'Top 10', value: 10 },
    { label: 'Top 25', value: 25 },
    { label: 'Top 50', value: 50 },
    { label: 'All Files', value: null }
  ];

  const getMostComplexFunctions = (): ComplexFunction[] => {
    if (!projectMetrics?.files) return [];
    
    const allFunctions: ComplexFunction[] = [];
    Object.entries(projectMetrics.files as Record<string, FileData>).forEach(([filePath, fileData]) => {
      if (fileData.functions) {
        fileData.functions.forEach((func) => {
          allFunctions.push({
            name: func.name || 'Unknown',
            module: filePath.split('/').pop()?.replace('.py', '') || 'Unknown',
            complexity: func.complexity || 0,
            lines: func.lines || 0
          });
        });
      }
    });
    
    return allFunctions
      .sort((a, b) => b.complexity - a.complexity)
      .slice(0, 10);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [metricsData, complexityData, issuesData] = await Promise.all([
          fetchDetailedMetrics(),
          fetchComplexityBreakdown(),
          fetchIssuesByCategory(),

        ]);
        setProjectMetrics(metricsData);
        setComplexityBreakdown(complexityData);
        setIssuesByCategory(issuesData);
        
        if (metricsData && metricsData.files) {
          const processedFiles = Object.entries(metricsData.files || {}).map(([filePath, fileData]: [string, any]) => {
            const issuesCount = Object.values(fileData.issues_by_category || {}).reduce(
              (sum: number, issues: any) => sum + (issues as any[]).length,
              0
            );
            const avgComplexity =
              fileData.functions && fileData.functions.length > 0
                ? Math.round(
                    (fileData.functions.reduce((sum: number, func: any) => sum + (func.complexity || 0), 0) /
                      fileData.functions.length) *
                      10
                  ) / 10
                : 0;
            return {
              path: filePath,
              name: filePath.split('/').pop(),
              lines: fileData.lines || 0,
              functions: fileData.functions?.length || 0,
              classes: fileData.classes?.length || 0,
              complexity: avgComplexity,
              issues: issuesCount,
            } as FileTableItem;
          });
          setFilesList(processedFiles);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching project metrics:', err);
        setError('Failed to load project metrics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (donutChartRef.current && issuesByCategory?.category_counts) renderIssuesDonutChart();
  }, [issuesByCategory]);

  useEffect(() => {
    if (barChartRef.current && complexityBreakdown?.total) renderComplexityBarChart();
  }, [complexityBreakdown]);

  const renderIssuesDonutChart = () => {
    if (!donutChartRef.current || !issuesByCategory?.category_counts) return;
    d3.select(donutChartRef.current).selectAll('*').remove();
    const width = 300,
      height = 300,
      margin = 40,
      radius = Math.min(width, height) / 2 - margin;
    const svg = d3
      .select(donutChartRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);
    const issueData = Object.entries(issuesByCategory.category_counts).map(([name, value]) => ({
      name,
      value: value as number,
    }));
    const categoryColors: { [key: string]: string } = {
      security: '#ef4444',
      style: '#3b82f6',
      duplication: '#10b981',
      code_smells: '#f59e0b',
      complexity: '#8b5cf6',
      sql_injection: '#ec4899',
    };
    const color = d3
      .scaleOrdinal<string>()
      .domain(issueData.map((d) => d.name))
      .range(issueData.map((d) => categoryColors[d.name] || '#6b7280'));
    const pie = d3.pie<any>().sort(null).value((d) => d.value);
    const arc = d3.arc().innerRadius(radius * 0.5).outerRadius(radius * 0.8);
    const outerArc = d3.arc().innerRadius(radius * 0.9).outerRadius(radius * 0.9);
    const arcs = svg
      .selectAll('allSlices')
      .data(pie(issueData))
      .enter()
      .append('path')
      .attr('d', arc as any)
      .attr('fill', (d) => color(d.data.name) as string)
      .attr('stroke', 'white')
      .style('stroke-width', '2px')
      .style('opacity', 0.7);
    arcs
      .append('title')
      .text(
        (d) =>
          `${d.data.name}: ${d.data.value} issues (${Math.round(
            (d.data.value / issueData.reduce((a, b) => a + b.value, 0)) * 100
          )}%)`
      );
    svg
      .selectAll('allPolylines')
      .data(pie(issueData))
      .enter()
      .append('polyline')
      .attr('stroke', 'black')
      .style('fill', 'none')
      .attr('stroke-width', 1)
      .attr('points', function (d) {
        const posA = arc.centroid(d as any),
          posB = outerArc.centroid(d as any),
          posC = outerArc.centroid(d as any);
        posC[0] =
          radius * 0.95 * (d.startAngle + (d.endAngle - d.startAngle) / 2 < Math.PI ? 1 : -1);
        return `${posA[0]},${posA[1]} ${posB[0]},${posB[1]} ${posC[0]},${posC[1]}`;
      });
    svg
      .selectAll('allLabels')
      .data(pie(issueData))
      .enter()
      .append('text')
      .text((d) => `${d.data.name} (${d.data.value})`)
      .attr('transform', function (d) {
        const pos = outerArc.centroid(d as any);
        pos[0] = radius * 0.99 * (d.startAngle + (d.endAngle - d.startAngle) / 2 < Math.PI ? 1 : -1);
        return `translate(${pos})`;
      })
      .style('text-anchor', (d) =>
        d.startAngle + (d.endAngle - d.startAngle) / 2 < Math.PI ? 'start' : 'end'
      )
      .style('font-size', '12px');
    const totalIssues = issueData.reduce((sum, item) => sum + item.value, 0);
    svg
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .text(`${totalIssues} Issues`);
  };

  const renderComplexityBarChart = () => {
    if (!barChartRef.current || !complexityBreakdown?.total) return;
    d3.select(barChartRef.current).selectAll('*').remove();
    const width = 450,
      height = 300,
      margin = { top: 30, right: 30, bottom: 70, left: 90 };
    const innerWidth = width - margin.left - margin.right,
      innerHeight = height - margin.top - margin.bottom;
    const svg = d3
      .select(barChartRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    const data = Object.entries(complexityBreakdown.total)
      .map(([name, value]) => ({
        name: name.replace(/_/g, ' '),
        value: value as number,
      }))
      .filter((item) => item.value > 0)
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
    const x = d3.scaleLinear().domain([0, d3.max(data, (d) => d.value) as number]).range([0, innerWidth]);
    const y = d3.scaleBand().domain(data.map((d) => d.name)).range([0, innerHeight]).padding(0.2);
    svg.append('g').attr('transform', `translate(0,${innerHeight})`).call(d3.axisBottom(x));
    svg.append('g').call(d3.axisLeft(y));
    svg
      .selectAll('bars')
      .data(data)
      .enter()
      .append('rect')
      .attr('y', (d) => y(d.name) as number)
      .attr('x', 0)
      .attr('height', y.bandwidth())
      .attr('width', (d) => x(d.value))
      .attr('fill', '#3b82f6');
    svg
      .selectAll('bar-values')
      .data(data)
      .enter()
      .append('text')
      .attr('y', (d) => (y(d.name) as number) + y.bandwidth() / 2 + 4)
      .attr('x', (d) => x(d.value) + 5)
      .attr('text-anchor', 'start')
      .text((d) => d.value)
      .style('font-size', '12px');
    svg
      .append('text')
      .attr('x', innerWidth / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text('Top Complexity Factors');
  };

  const calculateIssuesDensity = (): number => {
    const totalIssues = Object.values(issuesByCategory?.category_counts || {})
      .reduce((sum: number, count) => sum + (typeof count === 'number' ? count : 0), 0);
    const totalLines = projectMetrics?.project_metrics?.total_lines || 1;
    return (totalIssues / totalLines) * 50;
  };

  const calculateHealthScore = (): number => {
    if (!projectMetrics || !issuesByCategory) return 0;
    
    const issuesDensity = calculateIssuesDensity();
    const avgComplexity = projectMetrics.project_metrics?.avg_complexity || 0;
    const securityIssues = issuesByCategory.category_counts?.security || 0;
    
    let score = 100;
    
    score -= Math.min(30, issuesDensity * 4);
    score -= Math.min(20, avgComplexity * 3);  
    score -= Math.min(40, securityIssues * 10);
    
    return Math.max(0, Math.min(100, Math.round(score)));
  };
  
  const getHealthScoreColor = (score: number): string => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };
  
  const getHealthRating = (score: number): string => {
    if (score >= 80) return 'Good';
    if (score >= 60) return 'Needs improvement';
    return 'Critical issues';
  };

  const handleViewModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setViewMode(value === "null" ? null : parseInt(value, 10));
  };

  const getFilteredFiles = () => {
    const sortedFiles = [...filesList].sort((a, b) => b.issues - a.issues);
    
    if (viewMode !== null) {
      return sortedFiles.slice(0, viewMode);
    }
    return sortedFiles;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading project metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen flex-col">
        <div className="text-xl text-red-600 mb-4">Error loading project metrics</div>
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

  const filteredFiles = getFilteredFiles();
  const totalFiles = filesList.length;

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Project Metrics</h1>
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Back to Visualization
        </button>
      </div>
      <div className="bg-white shadow-md rounded-xl p-6">
        {projectMetrics ? (
          <div>
            <h3 className="text-xl font-semibold mb-6">Project-Wide Metrics Dashboard</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-md border">
                <h3 className="text-gray-500 text-sm font-medium">Total Files</h3>
                <p className="text-3xl font-bold mt-2">{projectMetrics?.project_metrics?.total_files || 0}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-md border">
                <h3 className="text-gray-500 text-sm font-medium">Total Lines of Code</h3>
                <p className="text-3xl font-bold mt-2">
                  {projectMetrics?.project_metrics?.total_lines?.toLocaleString() || 0}
                </p>
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

            <div className="bg-white p-6 rounded-lg shadow-md border relative group">
              <h3 className="text-gray-500 text-sm font-medium">Code Health Score</h3>
              <div className="flex items-end gap-2">
                <p className="text-3xl font-bold mt-2" style={{ 
                  color: getHealthScoreColor(calculateHealthScore()) 
                }}>
                  {calculateHealthScore()}/100
                </p>
                <div className="text-sm text-gray-500 mb-1">
                  {getHealthRating(calculateHealthScore())}
                </div>
              </div>
              
              <div className="absolute top-4 right-4 cursor-help">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                
                <div className="hidden group-hover:block absolute right-0 w-72 bg-gray-800 text-white text-xs rounded p-3 z-10">
                  <p className="font-bold mb-1">Code Health Score Calculation:</p>
                  <ul className="list-disc pl-4 space-y-1">
                    <li>Starting score: 100 points</li>
                    <li>Issues density: -{Math.min(30, 
                      parseFloat(((calculateIssuesDensity() * 2)).toFixed(1))
                    )} points</li>
                    <li>Code complexity: -{Math.min(20, 
                      parseFloat(((projectMetrics?.project_metrics?.avg_complexity || 0) * 1.5).toFixed(1))
                    )} points</li>
                    <li>Security issues: -{Math.min(40, 
                      parseFloat(((issuesByCategory?.category_counts?.security || 0) * 5).toFixed(1))
                    )} points</li>
                  </ul>
                  <div className="mt-2 pt-2 border-t border-gray-600">
                    <p>80-100: Good code health</p>
                    <p>60-79: Needs improvement</p>
                    <p>&lt;60: Critical issues</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md border mt-8 mb-8">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">All Project Files</h3>
                <div className="flex items-center">
                  <label htmlFor="viewMode" className="mr-2 text-gray-700">Show:</label>
                  <select 
                    id="viewMode" 
                    value={viewMode === null ? "null" : viewMode.toString()}
                    onChange={handleViewModeChange}
                    className="border rounded py-1 px-2"
                  >
                    {viewOptions.map(option => (
                      <option key={option.label} value={option.value === null ? "null" : option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
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
                    {filteredFiles.map((file: FileTableItem) => (
                      <tr
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
                          <span
                            className={`px-2 py-1 rounded-full text-white ${
                              file.issues > 0 ? 'bg-red-500' : 'bg-green-500'
                            }`}
                          >
                            {file.issues}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
             
              <div className="mt-4 text-gray-600 text-sm">
                Showing {filteredFiles.length} of {totalFiles} files
                {viewMode !== null && totalFiles > filteredFiles.length && (
                  <span> — Select "All Files" to view all</span>
                )}
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md border mb-8">
                <h3 className="text-lg font-semibold mb-4">Most Complex Functions</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="py-2 px-4 text-left">Function</th>
                        <th className="py-2 px-4 text-left">Module</th>
                        <th className="py-2 px-4 text-right">Complexity</th>
                        <th className="py-2 px-4 text-right">Lines</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getMostComplexFunctions().map((func, idx) => (
                        <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : ''}>
                          <td className="py-2 px-4">{func.name}</td>
                          <td className="py-2 px-4">{func.module}</td>
                          <td className="py-2 px-4 text-right">
                            <span className={func.complexity > 10 ? 'text-red-600 font-medium' : ''}>
                              {func.complexity}
                            </span>
                          </td>
                          <td className="py-2 px-4 text-right">{func.lines}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            
            
            {issuesByCategory?.category_counts && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                {Object.entries(issuesByCategory.category_counts).map(([category, count]) => {
                  const categoryColors: { [key: string]: string } = {
                    security: '#ef4444',
                    style: '#3b82f6',
                    duplication: '#10b981',
                    code_smells: '#f59e0b',
                    complexity: '#8b5cf6',
                    sql_injection: '#ec4899',
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
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-6 w-6"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            style={{ color: categoryColors[category] || '#718096' }}
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                            />
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
            <p className="text-gray-600">No project metrics available.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectMetricsPage;