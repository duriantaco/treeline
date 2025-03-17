import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import NodeConnections from '../src/components/NodeConnections';
import { CodeLink } from '../src/types';

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to} data-testid="mock-link">{children}</a>
  )
}));

describe('NodeConnections Component', () => {
  const mockIncomingLinks: CodeLink[] = [
    { 
      source: { id: 'id1', name: 'Module A', type: 'module' }, 
      target: 'target1', 
      type: 'imports' 
    },
    { 
      source: { id: 'id2', name: 'Module B', type: 'class' }, 
      target: 'target2', 
      type: 'contains' 
    }
  ];
  
  const mockOutgoingLinks: CodeLink[] = [
    { 
      source: 'source1', 
      target: { id: 'id3', name: 'Module C', type: 'function' }, 
      type: 'imports' 
    },
    { 
      source: 'source2', 
      target: { id: 'id4', name: 'Module D', type: 'class' }, 
      type: 'contains' 
    },
    { 
      source: 'source3', 
      target: { id: 'id5', name: 'Module E', type: 'module' }, 
      type: 'calls' 
    }
  ];
  
  const renderWithRouter = (ui: React.ReactElement) => {
    return render(ui, { wrapper: BrowserRouter });
  };
  
  test('renders without crashing', () => {
    renderWithRouter(<NodeConnections incoming={[]} outgoing={[]} />);
    expect(screen.getByText('🔄 Dependencies')).toBeInTheDocument();
  });
  
  test('does not display incoming section when there are no incoming links', () => {
    renderWithRouter(<NodeConnections incoming={[]} outgoing={mockOutgoingLinks} />);
    expect(screen.queryByText('Incoming (0)')).not.toBeInTheDocument();
  });
  
  test('does not display outgoing section when there are no outgoing links', () => {
    renderWithRouter(<NodeConnections incoming={mockIncomingLinks} outgoing={[]} />);
    expect(screen.queryByText('Outgoing (0)')).not.toBeInTheDocument();
  });
  
  test('displays incoming connections correctly', () => {
    renderWithRouter(<NodeConnections incoming={mockIncomingLinks} outgoing={[]} />);
    
    expect(screen.getByText(`Incoming (${mockIncomingLinks.length})`)).toBeInTheDocument();
    

    expect(screen.getAllByText('imports')).toHaveLength(1);
    expect(screen.getAllByText('contains')).toHaveLength(1);
    expect(screen.getAllByText('from')).toHaveLength(mockIncomingLinks.length); 
    expect(screen.getByText('Module A')).toBeInTheDocument();
    expect(screen.getByText('Module B')).toBeInTheDocument();
    
    const links = screen.getAllByTestId('mock-link');
    expect(links[0]).toHaveAttribute('href', '/node/id1');
    expect(links[1]).toHaveAttribute('href', '/node/id2');
  });
  
  test('displays outgoing connections correctly', () => {
    renderWithRouter(<NodeConnections incoming={[]} outgoing={mockOutgoingLinks} />);
    
    expect(screen.getByText(`Outgoing (${mockOutgoingLinks.length})`)).toBeInTheDocument();
    
    expect(screen.getByText('imports')).toBeInTheDocument();
    expect(screen.getByText('contains')).toBeInTheDocument();
    expect(screen.getByText('calls')).toBeInTheDocument();
    expect(screen.getAllByText('to').length).toBe(3);
    expect(screen.getByText('Module C')).toBeInTheDocument();
    expect(screen.getByText('Module D')).toBeInTheDocument();
    expect(screen.getByText('Module E')).toBeInTheDocument();
    
    const links = screen.getAllByTestId('mock-link');
    expect(links[0]).toHaveAttribute('href', '/node/id3');
    expect(links[1]).toHaveAttribute('href', '/node/id4');
    expect(links[2]).toHaveAttribute('href', '/node/id5');
  });
  
  test('displays both incoming and outgoing connections', () => {
    renderWithRouter(
      <NodeConnections 
        incoming={mockIncomingLinks} 
        outgoing={mockOutgoingLinks} 
      />
    );
    
    expect(screen.getByText(`Incoming (${mockIncomingLinks.length})`)).toBeInTheDocument();
    expect(screen.getByText(`Outgoing (${mockOutgoingLinks.length})`)).toBeInTheDocument();
    
    expect(screen.getByText('Module A')).toBeInTheDocument();
    expect(screen.getByText('Module B')).toBeInTheDocument();
    expect(screen.getByText('Module C')).toBeInTheDocument();
    expect(screen.getByText('Module D')).toBeInTheDocument();
    expect(screen.getByText('Module E')).toBeInTheDocument();
    
    expect(screen.getAllByText('imports').length).toBe(2);
    expect(screen.getAllByText('contains').length).toBe(2);
    expect(screen.getByText('calls')).toBeInTheDocument();
  });
  
  test('applies correct CSS classes for link types', () => {
    renderWithRouter(
      <NodeConnections 
        incoming={[mockIncomingLinks[0]]} 
        outgoing={[mockOutgoingLinks[2]]} 
      />
    );
    
    const linkTypeElements = document.querySelectorAll('.link-type');
    
    expect(linkTypeElements[0]).toHaveClass('imports');
    expect(linkTypeElements[0]).toHaveTextContent('imports');
    
    expect(linkTypeElements[1]).toHaveClass('calls');
    expect(linkTypeElements[1]).toHaveTextContent('calls');
  });
  
  test('handles mixed node formats correctly', () => {
    const mixedIncoming: CodeLink[] = [
      { 
        source: 'plain-id-1', 
        target: { id: 'target-id-1', name: 'Target Name 1', type: 'module' }, 
        type: 'imports' 
      },
      { 
        source: { id: 'object-id-2', name: 'Source Name 2', type: 'function' }, 
        target: 'target-id-2', 
        type: 'calls' 
      }
    ];
    
    renderWithRouter(<NodeConnections incoming={mixedIncoming} outgoing={[]} />);
    
    const links = screen.getAllByTestId('mock-link');
    expect(links[0]).toHaveAttribute('href', '/node/plain-id-1');
    expect(links[0].textContent).toBe('plain-id-1');
    
    expect(links[1]).toHaveAttribute('href', '/node/object-id-2');
    expect(links[1].textContent).toBe('Source Name 2');
  });
});