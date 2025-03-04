import React from 'react';

interface Issue {
  description: string;
  line?: number;
  file_path?: string;
  category?: string;
  [key: string]: any;
}

interface IssueCategoryDisplayProps {
  category: string;
  issues: Issue[];
  maxDisplay?: number;
  showFilePaths?: boolean;
  onIssueClick?: (issue: Issue) => void;
}

/**
 * Displays a list of code quality issues for a specific category
 * 
 * @param category - The category name of issues (e.g. 'security', 'style')
 * @param issues - Array of issue objects to display
 * @param maxDisplay - Maximum number of issues to show before truncating
 * @param showFilePaths - Whether to display file paths for each issue
 * @param onIssueClick - Optional callback when an issue is clicked
 */

const IssueCategoryDisplay: React.FC<IssueCategoryDisplayProps> = ({
  category,
  issues,
  maxDisplay = 5,
  showFilePaths = false,
  onIssueClick
}) => {
  if (!issues || issues.length === 0) return null;
  
  // Category styling configuration
  const categoryColors: {[key: string]: string} = {
    'security': '#ef4444',
    'style': '#3b82f6', 
    'duplication': '#10b981',
    'code_smells': '#f59e0b',
    'complexity': '#8b5cf6',
    'sql_injection': '#ec4899'
  };
  
  const categoryIcons: {[key: string]: string} = {
    'security': '🔒',
    'style': '🎨',
    'duplication': '🔄',
    'code_smells': '👃',
    'complexity': '🧩',
    'sql_injection': '💉'
  };

  const formattedCategoryName = category.replace(/_/g, ' ');
  const borderColor = categoryColors[category] || '#718096';
  const icon = categoryIcons[category] || '⚠️';
  
  const handleIssueClick = (issue: Issue) => {
    if (onIssueClick) {
      onIssueClick(issue);
    }
  };

  return (
    <div 
      className="border-l-4 p-4 rounded-r-md bg-white shadow-sm hover:shadow transition-shadow duration-200"
      style={{ borderColor }}
    >
      <h4 className="font-medium flex items-center text-gray-800">
        <span className="mr-2">{icon}</span>
        <span className="capitalize">{formattedCategoryName}</span>
        <span className="ml-2 px-2 py-0.5 bg-gray-100 rounded-full text-sm text-gray-600">
          {issues.length}
        </span>
      </h4>
      
      <ul className="mt-3 space-y-2">
        {issues.slice(0, maxDisplay).map((issue, index) => (
          <li 
            key={index} 
            className="flex items-start hover:bg-gray-50 p-1 rounded cursor-pointer"
            onClick={() => handleIssueClick(issue)}
          >
            <span className="mr-2 text-gray-400">•</span>
            <div className="flex-1">
              <span className="text-sm">{issue.description}</span>
              {(showFilePaths && issue.file_path) || issue.line ? (
                <div className="flex justify-between mt-1 text-xs text-gray-500">
                  {showFilePaths && issue.file_path && (
                    <span className="truncate mr-4 max-w-xs">
                      {issue.file_path.split('/').pop()}
                    </span>
                  )}
                  {issue.line && <span>Line {issue.line}</span>}
                </div>
              ) : null}
            </div>
          </li>
        ))}
        
        {issues.length > maxDisplay && (
          <li className="text-gray-500 italic text-sm mt-2 pl-2">
            ...and {issues.length - maxDisplay} more issues
          </li>
        )}
      </ul>
    </div>
  );
};

export default IssueCategoryDisplay;