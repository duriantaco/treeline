import React from 'react';

interface Issue {
  category: string;
  description: string;
  line: number | null;
  source: string;
}

interface NodeIssuesProps {
  securityIssues: Issue[];
  sqlInjectionIssues: Issue[];
  complexityIssues: Issue[];
  codeSmellIssues: Issue[];
  styleIssues: Issue[];
  duplicationIssues: Issue[];
  totalIssues: number;
}

const NodeIssues: React.FC<NodeIssuesProps> = ({
  securityIssues,
  sqlInjectionIssues,
  complexityIssues,
  codeSmellIssues,
  styleIssues,
  duplicationIssues,
  totalIssues
}) => {
  
  const renderIssueList = (issues: Issue[], className: string, title: string) => {
    if (issues.length === 0) return null;
    
    return (
      <div className={className}>
        <div className="issue-title">{title} ({issues.length})</div>
        <ul className="issue-list">
          {issues.map((issue, index) => (
            <li key={index}>
              {issue.description}
              {issue.line && <span className="issue-line">Line {issue.line}</span>}
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  return (
    <div className="quality-issues">
      <h3>Quality Issues ({totalIssues})</h3>
      
      {renderIssueList(securityIssues, 'security-issues', 'Security Issues')}
      {renderIssueList(sqlInjectionIssues, 'security-issues', 'SQL Injection Issues')}
      {renderIssueList(complexityIssues, 'complexity-issues', 'Complexity Issues')}
      {renderIssueList(codeSmellIssues, 'code-smell-issues', 'Code Smells')}
      {renderIssueList(styleIssues, 'style-issues', 'Style Issues')}
      {renderIssueList(duplicationIssues, 'duplication-issues', 'Duplication Issues')}
    </div>
  );
};

export default NodeIssues;