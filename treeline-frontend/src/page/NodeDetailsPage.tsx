import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchNodeData } from '../services/dataServices';
import ImpactAnalysis from '../components/ImpactAnalysis';

interface ConnectionLink {
  source_id: string;
  source_name: string;
  source_type: string;
  target_id: string;
  target_name: string;
  target_type: string;
  type: string;
  source_docstring?: string;
  target_docstring?: string;
  source_file_path?: string;
  target_file_path?: string;
}

interface NodeDetails {
  node: any;
  connections: {
    incoming: ConnectionLink[];
    outgoing: ConnectionLink[];
  };
  file_content: string | null;
}

const NodeDetailsPage: React.FC = () => {
  const { nodeId } = useParams<{ nodeId: string }>();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [nodeData, setNodeData] = useState<NodeDetails | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loadNodeData = async () => {
      if (!nodeId) return;

      try {
        setLoading(true);
        const data = await fetchNodeData(nodeId);

        const updatedIncoming = await Promise.all(
          data.connections.incoming.map(async (link: ConnectionLink) => {
            try {
              const sourceNode = await fetchNodeData(link.source_id);
              return {
                ...link,
                source_docstring: sourceNode?.node?.docstring || 'No docstring available',
                source_file_path: sourceNode?.node?.file_path || 'Unknown file',
              };
            } catch (err) {
              console.warn(`Could not fetch data for source node ${link.source_id}:`, err);
              return {
                ...link,
                source_docstring: 'No docstring available',
                source_file_path: 'Unknown file',
              };
            }
          })
        );
        
        const updatedOutgoing = await Promise.all(
          data.connections.outgoing.map(async (link: ConnectionLink) => {
            try {
              const targetNode = await fetchNodeData(link.target_id);
              return {
                ...link,
                target_docstring: targetNode?.node?.docstring || 'No docstring available',
                target_file_path: targetNode?.node?.file_path || 'Unknown file',
              };
            } catch (err) {
              console.warn(`Could not fetch data for target node ${link.target_id}:`, err);
              return {
                ...link,
                target_docstring: 'No docstring available',
                target_file_path: 'Unknown file',
              };
            }
          })
        );

        setNodeData({
          ...data,
          connections: {
            incoming: updatedIncoming,
            outgoing: updatedOutgoing,
          },
        });
        setError(null);
      } catch (err) {
        console.error('Error loading node data:', err);
        setError('Failed to load node details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadNodeData();
  }, [nodeId]);

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

  const formatConnections = (connections: NodeDetails['connections']) => {
    if (!connections || (connections.incoming.length === 0 && connections.outgoing.length === 0)) {
      return (
        <div className="mb-6">
          <h3 className="text-green-600 font-semibold text-lg flex items-center mb-2">
            <span className="mr-2">🔄</span>
            Dependencies
          </h3>
          <p className="text-gray-700">No dependencies found.</p>
        </div>
      );
    }

    return (
      <div className="mb-6">
        <h3 className="text-green-600 font-semibold text-lg flex items-center mb-4">
          <span className="mr-2">🔄</span>
          Dependencies
        </h3>

        {connections.incoming.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium mb-2">Incoming Connections ({connections.incoming.length})</h4>
            <p className="text-sm text-gray-600 mb-2">
              These are nodes that depend on or reference this node (e.g., functions or scripts that call or import this node).
            </p>
            <ul className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-md">
              {connections.incoming.map((link, index) => (
                <li key={index} className="mb-4 last:mb-0">
                  <div className="flex items-center mb-1">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded text-xs mr-2 ${
                        link.type === 'imports'
                          ? 'bg-purple-100 text-purple-800'
                          : link.type === 'contains'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-orange-100 text-orange-800'
                      }`}
                      title={
                        link.type === 'imports'
                          ? 'This node is imported by another node'
                          : link.type === 'contains'
                          ? 'This node contains another node'
                          : link.type === 'calls'
                          ? 'This node calls another node'
                          : 'General relationship between nodes'
                      }
                    >
                      {link.type}
                    </span>
                    <span className="text-sm">
                      {link.type === 'imports'
                        ? 'imported by'
                        : link.type === 'contains'
                        ? 'contained in'
                        : link.type === 'calls'
                        ? 'called by'
                        : 'related to'}{' '}
                      <button
                        onClick={() => navigate(`/node/${link.source_id}`)}
                        className="font-medium text-blue-600 hover:underline"
                      >
                        {link.source_name}
                      </button>
                      <span className="text-xs text-gray-500 ml-2">
                        (in {link.source_file_path})
                      </span>
                    </span>
                  </div>
                  {link.source_docstring && (
                    <div className="text-xs text-gray-600 italic mt-1">
                      <strong>Docstring:</strong> {link.source_docstring}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {connections.outgoing.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Outgoing Connections ({connections.outgoing.length})</h4>
            <p className="text-sm text-gray-600 mb-2">
              These are nodes that this node depends on or references (e.g., functions or scripts that this node calls or imports).
            </p>
            <ul className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-md">
              {connections.outgoing.map((link, index) => (
                <li key={index} className="mb-4 last:mb-0">
                  <div className="flex items-center mb-1">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded text-xs mr-2 ${
                        link.type === 'imports'
                          ? 'bg-purple-100 text-purple-800'
                          : link.type === 'contains'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-orange-100 text-orange-800'
                      }`}
                      title={
                        link.type === 'imports'
                          ? 'This node is imported by another node'
                          : link.type === 'contains'
                          ? 'This node contains another node'
                          : link.type === 'calls'
                          ? 'This node calls another node'
                          : 'General relationship between nodes'
                      }
                    >
                      {link.type}
                    </span>
                    <span className="text-sm">
                      {link.type === 'imports'
                        ? 'imports'
                        : link.type === 'contains'
                        ? 'contains'
                        : link.type === 'calls'
                        ? 'calls'
                        : 'relates to'}{' '}
                      <button
                        onClick={() => navigate(`/node/${link.target_id}`)}
                        className="font-medium text-blue-600 hover:underline"
                      >
                        {link.target_name}
                      </button>
                      <span className="text-xs text-gray-500 ml-2">
                        (in {link.target_file_path})
                      </span>
                    </span>
                  </div>
                  {link.target_docstring && (
                    <div className="text-xs text-gray-600 italic mt-1">
                      <strong>Docstring:</strong> {link.target_docstring}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderImpactAnalysis = (nodeData: NodeDetails) => {
    if (!nodeData || !nodeData.connections) {
      return (
        <div className="bg-gray-50 border-l-4 border-gray-300 p-4 rounded-r-md mb-6">
          <p className="text-gray-700">No connection data available for impact analysis.</p>
        </div>
      );
    }

    const { node, connections } = nodeData;

    return (
      <div className="bg-white shadow-md rounded-xl p-6 mb-6">
        <h3 className="text-indigo-600 font-semibold text-lg flex items-center mb-4">
          <span className="mr-2">🔄</span>
          Change Impact Analysis
        </h3>
        <ImpactAnalysis
          nodeId={nodeId || ''}
          nodeName={node.name}
          nodeType={node.type}
          connections={connections}
          hasIssues={node.code_smells && node.code_smells.length > 0}
          highComplexity={
            node.metrics &&
            ((node.metrics.complexity && node.metrics.complexity > 10) ||
              (node.metrics.cognitive_complexity && node.metrics.cognitive_complexity > 15))
          }
        />
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading node details...</div>
      </div>
    );
  }

  if (error || !nodeData) {
    return (
      <div className="flex items-center justify-center h-screen flex-col">
        <div className="text-xl text-red-600 mb-4">Error loading node details</div>
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

  const { node, connections } = nodeData;
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

          {node.is_entry && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-amber-100 text-amber-800 border border-amber-300">
              <span className="mr-1">🚪</span>
              Entry point
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
          <div className="mb-0 bg-gray-50 p-4 border-l-4 border-gray-300 rounded-r-md">
            <p className="italic text-gray-600">{node.docstring}</p>
          </div>
        )}
      </div>

      <div className="bg-white shadow-md rounded-xl p-6">
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Overview</h2>
          {hasIssues && formatIssues(node.code_smells)}

          {node.metrics && (
            <div className="mb-6">
              <h3 className="text-blue-600 font-semibold text-lg flex items-center mb-4">
                <span className="mr-2">📊</span>
                Summary
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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

                <div className="p-4 rounded-lg border bg-blue-50 border-blue-300">
                  <div className="text-sm text-gray-600">Dependencies</div>
                  <div className="text-2xl font-bold text-blue-700">
                    {connections.incoming.length + connections.outgoing.length}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-green-600 font-semibold text-lg flex items-center mb-4">
                <span className="mr-2">🔄</span>
                Dependencies Overview
              </h3>
              <div className="bg-green-50 border-green-300 border p-4 rounded-md">
                {connections.incoming.length === 0 && connections.outgoing.length === 0 ? (
                  <p className="text-gray-700">No dependencies found.</p>
                ) : (
                  <div>
                    <div className="flex justify-between border-b pb-2 mb-2">
                      <span className="font-medium">Incoming:</span>
                      <span className="font-bold text-blue-700">{connections.incoming.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Outgoing:</span>
                      <span className="font-bold text-green-700">{connections.outgoing.length}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

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

        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Dependencies</h2>
          {formatConnections(connections)}
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Impact Analysis</h2>
          {renderImpactAnalysis(nodeData)}
        </div>
      </div>
    </div>
  );
};

export default NodeDetailsPage;