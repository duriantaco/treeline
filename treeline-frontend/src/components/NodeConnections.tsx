import React from 'react';
import { Link } from 'react-router-dom';
import { CodeLink } from '../types';

interface NodeConnectionsProps {
  incoming: CodeLink[];
  outgoing: CodeLink[];
}

const NodeConnections: React.FC<NodeConnectionsProps> = ({ incoming, outgoing }) => {
  const getNodeName = (link: CodeLink, isSource: boolean): string => {
    const node = isSource ? link.source : link.target;
    return typeof node === 'object' ? node.name : node;
  };
  
  const getNodeId = (link: CodeLink, isSource: boolean): string => {
    const node = isSource ? link.source : link.target;
    return typeof node === 'object' ? node.id : node;
  };
  
  const renderConnectionList = (links: CodeLink[], isIncoming: boolean) => {
    if (links.length === 0) return null;
    
    return (
      <div className="connection-group">
        <h4>{isIncoming ? 'Incoming' : 'Outgoing'} ({links.length})</h4>
        <ul className="connection-list">
          {links.map((link, index) => (
            <li key={index}>
              <span className={`link-type ${link.type}`}>{link.type}</span>
              {isIncoming ? 'from' : 'to'} <Link to={`/node/${getNodeId(link, isIncoming)}`}>
                <strong>{getNodeName(link, isIncoming)}</strong>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  return (
    <div className="connections-section">
      <h3>🔄 Dependencies</h3>
      {renderConnectionList(incoming, true)}
      {renderConnectionList(outgoing, false)}
    </div>
  );
};

export default NodeConnections;