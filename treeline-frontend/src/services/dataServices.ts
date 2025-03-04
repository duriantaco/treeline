import { GraphData } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export interface GraphDataParams {
  limit?: number;
  offset?: number;
  minConnections?: number;
  types?: string[];
  searchTerm?: string;
  includeEntryPointsOnly?: boolean;
}

export async function fetchGraphData(params: GraphDataParams = {}): Promise<GraphData> {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());
    if (params.minConnections) queryParams.append('min_connections', params.minConnections.toString());
    if (params.types && params.types.length > 0) {
      params.types.forEach(type => queryParams.append('type', type));
    }
    if (params.searchTerm) queryParams.append('search', params.searchTerm);
    if (params.includeEntryPointsOnly) queryParams.append('entry_points_only', 'true');
    
    const queryString = queryParams.toString();
    const url = `${API_BASE_URL}/api/graph-data${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching graph data:', error);
    throw error;
  }
}

export async function fetchNodeData(nodeId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/node/${nodeId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        const errorData = await response.json();
        throw new Error(`Node not found: ${errorData.detail || 'The requested node does not exist'}`);
      }
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data for node ${nodeId}:`, error);
    throw error;
  }
}

export async function fetchNodeConnections(nodeId: string, depth: number = 1): Promise<any> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/node/${nodeId}/connections?depth=${depth}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching connections for node ${nodeId}:`, error);
    throw error;
  }
}

export async function fetchGraphSummary(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph-summary`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching graph summary:', error);
    throw error;
  }
}

export async function searchNodes(query: string, limit: number = 20): Promise<any[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}&limit=${limit}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error searching nodes:', error);
    throw error;
  }
}

export async function fetchDetailedMetrics(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/detailed-metrics`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching detailed metrics:', error);
      throw error;
    }
  }
  

  export async function fetchFileDetailedMetrics(filePath: string): Promise<any> {
    try {
      const encodedPath = encodeURIComponent(filePath);
      const response = await fetch(`${API_BASE_URL}/api/detailed-metrics/file/${encodedPath}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching detailed metrics for file ${filePath}:`, error);
      throw error;
    }
  }
  
  export async function fetchComplexityBreakdown(byFile: boolean = false): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/detailed-metrics/complexity-breakdown?by_file=${byFile}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching complexity breakdown:', error);
      throw error;
    }
  }
  
 
  export async function fetchIssuesByCategory(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/detailed-metrics/issues-by-category`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching issues by category:', error);
      throw error;
    }
  }
  
  export async function fetchDetailedDependencyGraph(includeDetails: boolean = true): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/detailed-metrics/dependency-graph?include_details=${includeDetails}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching detailed dependency graph:', error);
      throw error;
    }
  }

  export async function getQualityIssuesSummary(): Promise<any> {
    try {
      const graphData = await fetchGraphData();
      
      const issuesByCategory: Record<string, any[]> = {};
      const filesWithIssues: Record<string, {file_path: string, issue_count: number, [key: string]: any}> = {};
      
      graphData.nodes.forEach(node => {
        if (node.code_smells && node.code_smells.length > 0) {
          node.code_smells.forEach((smell: any) => {
            const category = getIssueCategory(smell);
            if (!issuesByCategory[category]) {
              issuesByCategory[category] = [];
            }
            
            const issue = typeof smell === 'string' 
              ? { description: smell, file_path: node.file_path || node.id } 
              : { ...smell, file_path: smell.file_path || node.file_path || node.id };
              
            issuesByCategory[category].push(issue);
        
            const filePath = issue.file_path;
            if (filePath) {
              if (!filesWithIssues[filePath]) {
                filesWithIssues[filePath] = { 
                  file_path: filePath, 
                  issue_count: 0 
                };
              }
              
              filesWithIssues[filePath].issue_count++;
              
              if (!filesWithIssues[filePath][category]) {
                filesWithIssues[filePath][category] = 0;
              }
              filesWithIssues[filePath][category]++;
            }
          });
        }
      });
      
      const category_counts: Record<string, number> = {};
      Object.keys(issuesByCategory).forEach(category => {
        category_counts[category] = issuesByCategory[category].length;
      });
      
      const files_with_most_issues = Object.values(filesWithIssues)
        .sort((a, b) => b.issue_count - a.issue_count)
        .slice(0, 10);
      
      return {
        issues_by_category: issuesByCategory,
        category_counts,
        files_with_most_issues,
        total_issues: Object.values(category_counts).reduce((sum, count) => sum + count, 0)
      };
    } catch (error) {
      console.error('Error getting quality issues summary:', error);
      throw error;
    }
  }
  

  function getIssueCategory(smell: any): string {
    if (typeof smell === 'string') {
      if (smell.startsWith('[')) {
        const endIndex = smell.indexOf(']', 1);
        if (endIndex !== -1) {
          return smell.slice(1, endIndex).toLowerCase();
        }
      }
      if (smell.toLowerCase().includes('security')) return 'security';
      if (smell.toLowerCase().includes('sql injection')) return 'sql_injection';
      if (smell.toLowerCase().includes('complexity')) return 'complexity';
      if (smell.toLowerCase().includes('duplicate')) return 'duplication';
      if (smell.toLowerCase().includes('style')) return 'style';
      return 'code_smells';
    } else if (typeof smell === 'object') {
      if (smell.category) return smell.category.toLowerCase();
      
      const description = smell.description || smell.message || '';
      if (description.toLowerCase().includes('security')) return 'security';
      if (description.toLowerCase().includes('sql injection')) return 'sql_injection';
      if (description.toLowerCase().includes('complexity')) return 'complexity';
      if (description.toLowerCase().includes('duplicate')) return 'duplication';
      if (description.toLowerCase().includes('style')) return 'style';
    }
    return 'code_smells'; 
  }

  export async function getComplexityBreakdown(): Promise<any> {
    try {
      const graphData = await fetchGraphData();
      
      const complexityFactors: Record<string, number> = {
        'if_statements': 0,
        'for_loops': 0,
        'while_loops': 0,
        'try_blocks': 0,
        'except_blocks': 0,
        'boolean_operations': 0,
        'and_operations': 0, 
        'or_operations': 0,
        'comprehensions': 0,
        'nested_functions': 0,
        'nested_classes': 0,
        'high_complexity': 0,
        'high_cognitive_complexity': 0,
        'high_nesting': 0
      };
      
      graphData.nodes.forEach(node => {
        if (node.metrics) {
          if (node.metrics.complexity && node.metrics.complexity > 10) {
            complexityFactors.high_complexity++;
          }
          
          if (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15) {
            complexityFactors.high_cognitive_complexity++;
          }
          
          if (node.metrics.nested_depth && node.metrics.nested_depth > 4) {
            complexityFactors.high_nesting++;
          }
          
          // rough estimation since can't directly count each factor
          if (node.metrics.complexity) {
            const complexity = node.metrics.complexity;
            complexityFactors.if_statements += Math.floor(complexity * 0.4);
            complexityFactors.for_loops += Math.floor(complexity * 0.2);
            complexityFactors.while_loops += Math.floor(complexity * 0.1);
            complexityFactors.boolean_operations += Math.floor(complexity * 0.2);
            complexityFactors.try_blocks += Math.floor(complexity * 0.1);
          }
        }
        
        if (node.code_smells) {
          node.code_smells.forEach((smell: any) => {
            const description = typeof smell === 'string' ? smell : (smell.description || '');
            
            if (description.toLowerCase().includes('nested')) {
              if (description.toLowerCase().includes('function')) {
                complexityFactors.nested_functions++;
              } else if (description.toLowerCase().includes('class')) {
                complexityFactors.nested_classes++;
              } else {
                complexityFactors.high_nesting++;
              }
            }
            
            if (description.toLowerCase().includes('comprehension')) {
              complexityFactors.comprehensions++;
            }
          });
        }
      });
      
      return { total: complexityFactors };
    } catch (error) {
      console.error('Error getting complexity breakdown:', error);
      throw error;
    }
  }
  

  export async function getProjectMetrics(): Promise<any> {
    try {
      const graphData = await fetchGraphData();
      
      const files = new Set<string>();
      let totalFunctions = 0;
      let totalClasses = 0;
      let totalLines = 0;
      let sumComplexity = 0;
      let complexFunctionsCount = 0;
      let maxComplexity = 0;
      
      const fileMetrics: Record<string, any> = {};
      
      graphData.nodes.forEach(node => {
        if (node.file_path) {
          files.add(node.file_path);
          
          if (!fileMetrics[node.file_path]) {
            fileMetrics[node.file_path] = {
              path: node.file_path,
              lines: 0,
              functions: [],
              classes: [],
              issues_by_category: {}
            };
          }
        }
        
        // Track metrics
        if (node.metrics) {
          if (node.metrics.lines) {
            totalLines += node.metrics.lines;
            
            if (node.file_path) {
              fileMetrics[node.file_path].lines = Math.max(
                fileMetrics[node.file_path].lines,
                node.metrics.lines
              );
            }
          }
          
          if (node.metrics.functions) {
            totalFunctions += node.metrics.functions;
          }
          
          if (node.metrics.classes) {
            totalClasses += node.metrics.classes;
          }
          
          if (node.metrics.complexity) {
            sumComplexity += node.metrics.complexity;
            maxComplexity = Math.max(maxComplexity, node.metrics.complexity);
            
            if (node.metrics.complexity > 10) {
              complexFunctionsCount++;
            }
          }
        }
        
        if (node.type === 'function' && node.file_path) {
          fileMetrics[node.file_path].functions.push({
            name: node.name,
            complexity: node.metrics?.complexity || 0,
            cognitive_complexity: node.metrics?.cognitive_complexity || 0,
            nested_depth: node.metrics?.nested_depth || 0,
            lines: node.metrics?.lines || 0,
            params: node.metrics?.params || 0,
            code_smells: node.code_smells || [],
            line: 0 
          });
        } else if (node.type === 'class' && node.file_path) {
          fileMetrics[node.file_path].classes.push({
            name: node.name,
            complexity: node.metrics?.complexity || 0,
            methods: node.methods || {},
            lines: node.metrics?.lines || 0,
            code_smells: node.code_smells || [],
            line: 0
          });
        }
        
        if (node.code_smells && node.code_smells.length > 0 && node.file_path && typeof node.file_path === 'string') {
          const filePath = node.file_path;
          node.code_smells.forEach((smell: any) => {
            const category = getIssueCategory(smell);
            
            if (!fileMetrics[filePath].issues_by_category[category]) {
              fileMetrics[filePath].issues_by_category[category] = [];
            }
            
            const issue = typeof smell === 'string' 
              ? { description: smell } 
              : smell;
              
            fileMetrics[filePath].issues_by_category[category].push(issue);
          });
        }
      });
      
      const totalFunctionNodes = graphData.nodes.filter(n => n.type === 'function').length;
      const totalClassNodes = graphData.nodes.filter(n => n.type === 'class').length;
      const totalModuleNodes = graphData.nodes.filter(n => n.type === 'module').length;
      
      const nodeCount = graphData.nodes.length;
      const avgComplexity = sumComplexity / 
        (graphData.nodes.filter(n => n.metrics?.complexity !== undefined).length || 1);
      
      return {
        files: fileMetrics,
        project_metrics: {
          total_files: files.size || totalModuleNodes,
          total_functions: totalFunctions || totalFunctionNodes,
          total_classes: totalClasses || totalClassNodes,
          total_lines: totalLines,
          avg_complexity: avgComplexity.toFixed(2),
          complex_functions_count: complexFunctionsCount,
          max_complexity: maxComplexity
        },
        dependency_metrics: {
          entry_points: graphData.nodes.filter(n => n.is_entry).length,
          nodes: nodeCount,
          links: graphData.links.length,
          avg_dependencies: (graphData.links.length / nodeCount).toFixed(2)
        }
      };
    } catch (error) {
      console.error('Error getting project metrics:', error);
      throw error;
    }
  }