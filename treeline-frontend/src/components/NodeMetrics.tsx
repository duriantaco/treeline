import React from 'react';

interface NodeMetricsProps {
  metrics: {
    complexity?: number | string;
    cognitive_complexity?: number | string;
    lines?: number | string;
    functions?: number | string;
    classes?: number | string;
    params?: number | string;
    methods?: number | string;
    nested_depth?: number | string;
    [key: string]: any;
  };
}

const NodeMetrics: React.FC<NodeMetricsProps> = ({ metrics }) => {
  const isWarning = (key: string, value: any): boolean => {
    if (typeof value !== 'number') return false;
    
    switch (key) {
      case 'complexity':
        return value > 10;
      case 'cognitive_complexity':
        return value > 15;
      case 'lines':
        return value > 100;
      case 'params':
        return value > 5;
      case 'methods':
        return value > 20;
      case 'nested_depth':
        return value > 4;
      default:
        return false;
    }
  };
  
  const formatKey = (key: string): string => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  };
  
  return (
    <div className="metrics-section">
      <h3>📊 Detailed Metrics</h3>
      <table className="metrics-table">
        <tbody>
          {Object.entries(metrics).map(([key, value]) => {
            if (key.startsWith('_')) return null;
            
            const formattedKey = formatKey(key);
            const warning = isWarning(key, value);
            
            return (
              <tr key={key} className={warning ? 'metric-warning' : ''}>
                <td>{formattedKey}</td>
                <td>{value}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default NodeMetrics;