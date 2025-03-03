export interface CodeNode {
    id: string;
    name: string;
    type: 'module' | 'class' | 'function';
    is_entry?: boolean;
    docstring?: string;
    code_smells?: Array<string | CodeSmell>;
    security_issues?: Array<string | CodeSmell>;
    complexity_issues?: Array<string | CodeSmell>;
    duplication_issues?: Array<string | CodeSmell>;
    metrics?: {
      complexity?: number;
      cognitive_complexity?: number;
      lines?: number;
      functions?: number;
      classes?: number;
      params?: number;
      methods?: number;
      nested_depth?: number;
      [key: string]: any;
    };
    methods?: {
      [key: string]: any;
    };
    x?: number;
    y?: number;
    vx?: number;
    vy?: number;
    fx?: number | null;
    fy?: number | null;
  }
  
  export interface CodeLink {
    source: string | CodeNode;
    target: string | CodeNode;
    type: 'imports' | 'contains' | 'calls';
  }
  
  export interface CodeSmell {
    category?: string;
    description?: string;
    message?: string;
    line?: number | null;
    lineno?: number | null;
  }
  
  export interface GraphData {
    nodes: CodeNode[];
    links: CodeLink[];
  }
  
  export interface Issue {
    category: string;
    description: string;
    line: number | null;
    source: string;
  }