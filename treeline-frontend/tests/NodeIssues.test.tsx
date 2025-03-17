import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import NodeIssues from '../src/components/NodeIssues';

describe('NodeIssues Component', () => {
  const mockSecurityIssues = [
    { category: 'security', description: 'Insecure password handling', line: 42, source: 'file.js' },
    { category: 'security', description: 'XSS vulnerability', line: 78, source: 'file.js' }
  ];
  
  const mockSqlInjectionIssues = [
    { category: 'sql', description: 'Potential SQL injection', line: 15, source: 'file.js' }
  ];
  
  const mockComplexityIssues = [
    { category: 'complexity', description: 'Function has high complexity', line: 100, source: 'file.js' },
    { category: 'complexity', description: 'Excessive nesting depth', line: 125, source: 'file.js' },
    { category: 'complexity', description: 'Too many parameters', line: 200, source: 'file.js' }
  ];
  
  const mockCodeSmellIssues = [
    { category: 'smell', description: 'Unused variable', line: 45, source: 'file.js' },
    { category: 'smell', description: 'Magic number', line: null, source: 'file.js' }
  ];
  
  const mockStyleIssues = [
    { category: 'style', description: 'Missing semicolon', line: 10, source: 'file.js' }
  ];
  
  const mockDuplicationIssues = [
    { category: 'duplication', description: 'Duplicate code with file2.js', line: null, source: 'file.js' }
  ];
  
  test('renders without crashing', () => {
    render(
      <NodeIssues 
        securityIssues={[]} 
        sqlInjectionIssues={[]} 
        complexityIssues={[]} 
        codeSmellIssues={[]}
        styleIssues={[]}
        duplicationIssues={[]}
        totalIssues={0}
      />
    );
    expect(screen.getByText('Quality Issues (0)')).toBeInTheDocument();
  });
  
  test('displays total issues count correctly', () => {
    const totalIssues = 
      mockSecurityIssues.length + 
      mockSqlInjectionIssues.length + 
      mockComplexityIssues.length + 
      mockCodeSmellIssues.length +
      mockStyleIssues.length +
      mockDuplicationIssues.length;
    
    render(
      <NodeIssues 
        securityIssues={mockSecurityIssues} 
        sqlInjectionIssues={mockSqlInjectionIssues} 
        complexityIssues={mockComplexityIssues} 
        codeSmellIssues={mockCodeSmellIssues}
        styleIssues={mockStyleIssues}
        duplicationIssues={mockDuplicationIssues}
        totalIssues={totalIssues}
      />
    );
    expect(screen.getByText(`Quality Issues (${totalIssues})`)).toBeInTheDocument();
  });
  
  test('displays security issues correctly', () => {
    render(
      <NodeIssues 
        securityIssues={mockSecurityIssues} 
        sqlInjectionIssues={[]} 
        complexityIssues={[]} 
        codeSmellIssues={[]}
        styleIssues={[]}
        duplicationIssues={[]}
        totalIssues={mockSecurityIssues.length}
      />
    );
    
    expect(screen.getByText(`Security Issues (${mockSecurityIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText('Insecure password handling')).toBeInTheDocument();
    expect(screen.getByText('XSS vulnerability')).toBeInTheDocument();
    expect(screen.getByText('Line 42')).toBeInTheDocument();
    expect(screen.getByText('Line 78')).toBeInTheDocument();
  });
  
  test('displays SQL injection issues correctly', () => {
    render(
      <NodeIssues 
        securityIssues={[]} 
        sqlInjectionIssues={mockSqlInjectionIssues} 
        complexityIssues={[]} 
        codeSmellIssues={[]}
        styleIssues={[]}
        duplicationIssues={[]}
        totalIssues={mockSqlInjectionIssues.length}
      />
    );
    
    expect(screen.getByText(`SQL Injection Issues (${mockSqlInjectionIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText('Potential SQL injection')).toBeInTheDocument();
    expect(screen.getByText('Line 15')).toBeInTheDocument();
  });
  
  test('displays complexity issues correctly', () => {
    render(
      <NodeIssues 
        securityIssues={[]} 
        sqlInjectionIssues={[]} 
        complexityIssues={mockComplexityIssues} 
        codeSmellIssues={[]}
        styleIssues={[]}
        duplicationIssues={[]}
        totalIssues={mockComplexityIssues.length}
      />
    );
    
    expect(screen.getByText(`Complexity Issues (${mockComplexityIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText('Function has high complexity')).toBeInTheDocument();
    expect(screen.getByText('Excessive nesting depth')).toBeInTheDocument();
    expect(screen.getByText('Too many parameters')).toBeInTheDocument();
    expect(screen.getByText('Line 100')).toBeInTheDocument();
    expect(screen.getByText('Line 125')).toBeInTheDocument();
    expect(screen.getByText('Line 200')).toBeInTheDocument();
  });
  
  test('displays code smell issues correctly', () => {
    render(
      <NodeIssues 
        securityIssues={[]} 
        sqlInjectionIssues={[]} 
        complexityIssues={[]} 
        codeSmellIssues={mockCodeSmellIssues}
        styleIssues={[]}
        duplicationIssues={[]}
        totalIssues={mockCodeSmellIssues.length}
      />
    );
    
    expect(screen.getByText(`Code Smells (${mockCodeSmellIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText('Unused variable')).toBeInTheDocument();
    expect(screen.getByText('Magic number')).toBeInTheDocument();
    expect(screen.getByText('Line 45')).toBeInTheDocument();
    expect(screen.queryByText('Line null')).not.toBeInTheDocument();
  });
  
  test('displays style issues correctly', () => {
    render(
      <NodeIssues 
        securityIssues={[]} 
        sqlInjectionIssues={[]} 
        complexityIssues={[]} 
        codeSmellIssues={[]}
        styleIssues={mockStyleIssues}
        duplicationIssues={[]}
        totalIssues={mockStyleIssues.length}
      />
    );
    
    expect(screen.getByText(`Style Issues (${mockStyleIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText('Missing semicolon')).toBeInTheDocument();
    expect(screen.getByText('Line 10')).toBeInTheDocument();
  });
  
  test('displays duplication issues correctly', () => {
    render(
      <NodeIssues 
        securityIssues={[]} 
        sqlInjectionIssues={[]} 
        complexityIssues={[]} 
        codeSmellIssues={[]}
        styleIssues={[]}
        duplicationIssues={mockDuplicationIssues}
        totalIssues={mockDuplicationIssues.length}
      />
    );
    
    expect(screen.getByText(`Duplication Issues (${mockDuplicationIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText('Duplicate code with file2.js')).toBeInTheDocument();
    expect(screen.queryByText('Line null')).not.toBeInTheDocument();
  });
  
  test('does not display sections for empty issue arrays', () => {
    render(
      <NodeIssues 
        securityIssues={mockSecurityIssues} 
        sqlInjectionIssues={[]} //nothing
        complexityIssues={mockComplexityIssues} 
        codeSmellIssues={[]} //empty too
        styleIssues={mockStyleIssues}
        duplicationIssues={[]} 
        totalIssues={mockSecurityIssues.length + mockComplexityIssues.length + mockStyleIssues.length}
      />
    );
    
    // These sections should be visible
    expect(screen.getByText(`Security Issues (${mockSecurityIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText(`Complexity Issues (${mockComplexityIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText(`Style Issues (${mockStyleIssues.length})`)).toBeInTheDocument();
    
    // These sections should not be displayed
    expect(screen.queryByText('SQL Injection Issues (0)')).not.toBeInTheDocument();
    expect(screen.queryByText('Code Smells (0)')).not.toBeInTheDocument();
    expect(screen.queryByText('Duplication Issues (0)')).not.toBeInTheDocument();
  });
  
  test('displays multiple issue types together', () => {
    const totalIssues = mockSecurityIssues.length + mockSqlInjectionIssues.length;
    
    render(
      <NodeIssues 
        securityIssues={mockSecurityIssues} 
        sqlInjectionIssues={mockSqlInjectionIssues} 
        complexityIssues={[]} 
        codeSmellIssues={[]}
        styleIssues={[]}
        duplicationIssues={[]}
        totalIssues={totalIssues}
      />
    );
    
    expect(screen.getByText(`Quality Issues (${totalIssues})`)).toBeInTheDocument();
    expect(screen.getByText(`Security Issues (${mockSecurityIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText(`SQL Injection Issues (${mockSqlInjectionIssues.length})`)).toBeInTheDocument();
    expect(screen.getByText('Insecure password handling')).toBeInTheDocument();
    expect(screen.getByText('XSS vulnerability')).toBeInTheDocument();
    expect(screen.getByText('Potential SQL injection')).toBeInTheDocument();
  });
  
  test('handles zero total issues', () => {
    render(
      <NodeIssues 
        securityIssues={[]} 
        sqlInjectionIssues={[]} 
        complexityIssues={[]} 
        codeSmellIssues={[]}
        styleIssues={[]}
        duplicationIssues={[]}
        totalIssues={0}
      />
    );
    
    expect(screen.getByText('Quality Issues (0)')).toBeInTheDocument();
    expect(screen.queryByText('Security Issues')).not.toBeInTheDocument();
    expect(screen.queryByText('SQL Injection Issues')).not.toBeInTheDocument();
    expect(screen.queryByText('Complexity Issues')).not.toBeInTheDocument();
    expect(screen.queryByText('Code Smells')).not.toBeInTheDocument();
    expect(screen.queryByText('Style Issues')).not.toBeInTheDocument();
    expect(screen.queryByText('Duplication Issues')).not.toBeInTheDocument();
  });
});