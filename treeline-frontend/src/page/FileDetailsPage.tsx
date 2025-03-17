import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchNodeByFilePath } from '../services/dataServices';

interface StructureItem {
  type: string;
  name: string;
  line: number;
}

interface NodeDetails {
  node: {
    structure?: StructureItem[];
    [key: string]: any;
  };
  connections: {
    incoming: any[];
    outgoing: any[];
  };
  file_content: string | null;
}

const FileDetailsPage: React.FC = () => {
    const { filePath } = useParams<{ filePath: string }>();
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [nodeData, setNodeData] = useState<NodeDetails | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const loadNodeData = async () => {
          if (!filePath) return;
          try {
            setLoading(true);
            const decodedPath = decodeURIComponent(filePath);
            const data = await fetchNodeByFilePath(decodedPath);
            if (!data) {
              throw new Error("Failed to load file details.");
            }
            setNodeData(data);
            setError(null);
          } catch (err: any) {
            console.error("Error loading file data:", err);
            setError(err.message || "Failed to load file details.");
          } finally {
            setLoading(false);
          }
        };
        loadNodeData();
      }, [filePath]);

      const renderFileStructure = (nodeData: NodeDetails) => {
        if (!nodeData || !nodeData.node || !nodeData.node.structure) {
          return null;
        }
      
        const { structure } = nodeData.node;
        
        return (
          <div className="mb-6">
            <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-4">
              <span className="mr-2">📄</span>
              File Structure
            </h3>
            <div className="bg-gray-50 border-l-4 border-blue-500 p-4 rounded-r-md">
              {structure.length === 0 ? (
                <p className="text-gray-600">No classes or functions found</p>
              ) : (
                <ul className="space-y-2">
                  {structure.map((item, index) => (
                    <li key={index} className="flex items-start">
                      <span className={`inline-block px-2 py-1 rounded text-xs mr-2 ${
                        item.type === 'class' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {item.type}
                      </span>
                      <span className="font-medium">{item.name}</span>
                      <span className="text-gray-500 ml-2">Line {item.line}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        );
      };
      

  const getNodeTypePillClass = (type: string) => {
    switch (type) {
      case 'module':
        return 'bg-blue-100 text-blue-800';
      case 'class':
        return 'bg-cyan-100 text-cyan-800';
      case 'function':
        return 'bg-teal-100 text-teal-800';
      default:
        return '';
    }
  };

  const formatIssues = (issues: any[]) => {
    if (!issues || issues.length === 0) return null;

    return (
      <div className="mb-6">
        <h3 className="text-red-600 font-semibold text-lg flex items-center mb-2">
          <span className="mr-2">⚠️</span>
          Issues ({issues.length})
        </h3>
        <ul className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-md">
          {issues.map((issue, index) => (
            <li key={index} className="mb-2 last:mb-0 flex items-start">
              <span className="mr-2">•</span>
              <span>{typeof issue === 'string' ? issue : issue.description || issue.message}</span>
              {(issue.line || issue.lineno) && (
                <span className="text-gray-600 text-sm ml-auto">Line {issue.line || issue.lineno}</span>
              )}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading file details...</div>
      </div>
    );
  }

  if (error || !nodeData) {
    return (
      <div className="flex items-center justify-center h-screen flex-col">
        <div className="text-xl text-red-600 mb-4">Error loading file details</div>
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

  const { node } = nodeData;
  const hasIssues = node.code_smells && node.code_smells.length > 0;
  const highComplexity =
    node.metrics &&
    ((node.metrics.complexity && node.metrics.complexity > 10) ||
      (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15));

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-6 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          ← Back to Visualization
        </button>

        <div className="flex gap-2">
          {hasIssues && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-800 border border-red-300">
              <span className="mr-1">⚠️</span>
              {node.code_smells.length} issue{node.code_smells.length !== 1 ? 's' : ''}
            </span>
          )}

          {highComplexity && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-amber-100 text-amber-800 border border-amber-300">
              <span className="mr-1">🔄</span>
              High complexity
            </span>
          )}
        </div>
      </div>

      <div className="bg-white shadow-md rounded-xl p-6 mb-8">
        <h1 className="text-2xl font-bold flex flex-wrap items-center gap-2 mb-4">
          {node.name}
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${getNodeTypePillClass(node.type)}`}>
            {node.type}
          </span>
        </h1>

        {node.docstring && (
          <div className="mb-4 bg-gray-50 p-4 border-l-4 border-gray-300 rounded-r-md">
            <p className="italic text-gray-600">{node.docstring}</p>
          </div>
        )}
      </div>

      <div className="bg-white shadow-md rounded-xl p-6">
        {hasIssues && formatIssues(node.code_smells)}
        {renderFileStructure(nodeData)}
        
        {node.metrics && (
          <div className="mb-6">
            <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-4">
              <span className="mr-2">📊</span>
              Summary
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {node.metrics.complexity && (
                <div
                  className={`p-4 rounded-lg border ${
                    node.metrics.complexity > 10 ? 'bg-red-50 border-red-300' : 'bg-blue-50 border-blue-300'
                  }`}
                >
                  <div className="text-sm text-gray-600">Complexity</div>
                  <div
                    className={`text-2xl font-bold ${
                      node.metrics.complexity > 10 ? 'text-red-700' : 'text-blue-700'
                    }`}
                  >
                    {node.metrics.complexity}
                  </div>
                </div>
              )}

              {node.metrics.cognitive_complexity && (
                <div
                  className={`p-4 rounded-lg border ${
                    node.metrics.cognitive_complexity > 15 ? 'bg-red-50 border-red-300' : 'bg-blue-50 border-blue-300'
                  }`}
                >
                  <div className="text-sm text-gray-600">Cognitive Complexity</div>
                  <div
                    className={`text-2xl font-bold ${
                      node.metrics.cognitive_complexity > 15 ? 'text-red-700' : 'text-blue-700'
                    }`}
                  >
                    {node.metrics.cognitive_complexity}
                  </div>
                </div>
              )}

              {node.metrics.lines && (
                <div className="p-4 rounded-lg border bg-blue-50 border-blue-300">
                  <div className="text-sm text-gray-600">Lines</div>
                  <div className="text-2xl font-bold text-blue-700">{node.metrics.lines}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {node.metrics && (
          <div>
            <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-4">
              <span className="mr-2">📊</span>
              Key Metrics
            </h3>
            <div className="bg-blue-50 border-blue-300 border p-4 rounded-md">
              <div className="grid grid-cols-2 gap-4">
                {node.metrics.functions && (
                  <div>
                    <div className="text-sm text-gray-600">Functions</div>
                    <div className="font-bold">{node.metrics.functions}</div>
                  </div>
                )}

                {node.metrics.classes && (
                  <div>
                    <div className="text-sm text-gray-600">Classes</div>
                    <div className="font-bold">{node.metrics.classes}</div>
                  </div>
                )}

                {node.metrics.params && (
                  <div>
                    <div className="text-sm text-gray-600">Parameters</div>
                    <div className="font-bold">{node.metrics.params}</div>
                  </div>
                )}

                {node.metrics.nested_depth && (
                  <div>
                    <div className="text-sm text-gray-600">Nesting Depth</div>
                    <div className="font-bold">{node.metrics.nested_depth}</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileDetailsPage;