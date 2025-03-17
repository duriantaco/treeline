export interface FileMetricsIssue {
    description: string;
    line?: number;
  }
  
  export interface FileFunction {
    name: string;
    complexity?: number;
    cognitive_complexity?: number;
    nested_depth?: number;
    params?: number;
    lines?: number;
    code_smells?: FileMetricsIssue[];
  }
  
  export interface FileClass {
    name: string;
  }
  
  export interface IssuesByCategory {
    [category: string]: FileMetricsIssue[];
  }
  
  export interface FileInfo {
    lines?: number;
    functions: FileFunction[];
    classes: FileClass[];
    issues_by_category: IssuesByCategory;
  }
  
  export interface ProjectMetrics {
    total_files?: number;
    total_lines?: number;
    total_functions?: number;
    total_classes?: number;
    avg_complexity?: number;
    max_complexity?: number;
  }
  
  export interface MetricsData {
    project_metrics?: ProjectMetrics;
    files?: {
      [filePath: string]: FileInfo;
    };
  }
  
  export interface FileMetricsData extends FileInfo {
    path: string;
  }
  
  export interface ComplexityBreakdownData {
    total: {
      high_complexity?: number;
      high_cognitive_complexity?: number;
      high_nesting?: number;
      long_functions?: number;
      many_parameters?: number;
      [key: string]: number | undefined;
    };
  }
  
  export interface IssueFile {
    file_path: string;
    issue_count: number;
    security?: number;
    style?: number;
    duplication?: number;
    code_smells?: number;
    complexity?: number;
    sql_injection?: number;
    [category: string]: number | string | undefined;
  }
  
  export interface IssuesByCategoryData {
    category_counts: {
      [category: string]: number;
    };
    files_with_most_issues: IssueFile[];
  }
  
  export interface PreparedFileMetric {
    name: string;
    path: string;
    lines: number;
    functions: number;
    classes: number;
    issues: number;
    complexity: number;
  }