import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import Graph from '../src/components/Graph';
import '@testing-library/jest-dom';


jest.mock('d3', () => {
  const elements: {
    circles: ReturnType<typeof createSelection>[];
    lines: ReturnType<typeof createSelection>[];
  } = {
    circles: [],
    lines: []
  };
  
  const createNodeMock = (tag) => ({
    getBoundingClientRect: () => ({ width: 100, height: 100 }),
    tagName: tag
  });

  const createSelection = (tag, isRoot = false) => {
    type SelectionType = ReturnType<typeof createSelection>;
    const selection = {
      node: jest.fn(() => createNodeMock(tag)),
      append: jest.fn((t) => createSelection(t)),
      attr: jest.fn(() => selection),
      style: jest.fn(() => selection),
      on: jest.fn((event, handler) => {
        if (selection._elements) {
          selection._elements.forEach(el => {
            el._eventHandlers = el._eventHandlers || {};
            el._eventHandlers[event] = handler;
          });
        } else {
          selection._eventHandlers = selection._eventHandlers || {};
          selection._eventHandlers[event] = handler;
        }
        return selection;
      }),
      data: jest.fn((data) => {
        selection._data = data;
        return selection;
      }),
      enter: jest.fn(() => {
        const dataLength = selection._data ? selection._data.length : 0;
        return {
          append: jest.fn((newTag) => {
            const newElements: SelectionType[] = [];
            for (let i = 0; i < dataLength; i++) {
              const newElement = createSelection(newTag);
              newElement._datum = selection._data[i];
              newElements.push(newElement);
              if (newTag === 'circle') {
                elements.circles.push(newElement);
              } else if (newTag === 'line') {
                elements.lines.push(newElement);
              }
            }
            const multiSelection = createSelection(newTag);
            multiSelection._elements = newElements;
            return multiSelection;
          })
        };
      }),
      call: jest.fn(() => selection),
      remove: jest.fn(() => selection),
      select: jest.fn(() => createSelection(tag)),
      selectAll: jest.fn((selector) => {
        const newSelection = createSelection(selector.replace(/[.*]/g, ''));
        if (isRoot && selector === '*') {
          elements.circles = [];
          elements.lines = [];
        }
        return newSelection;
      })
    };
    return selection;
  };

  return {
    _elements: elements,
    select: jest.fn((node) => createSelection('svg', true)),
    forceSimulation: jest.fn((nodes) => ({
      force: jest.fn().mockReturnThis(),
      on: jest.fn((event, callback) => {
        if (event === 'tick') callback();
        return this;
      }),
      nodes: jest.fn().mockReturnThis(),
      alpha: jest.fn().mockReturnThis(),
      restart: jest.fn().mockReturnThis(),
      stop: jest.fn().mockReturnThis()
    })),
    forceLink: jest.fn(() => ({ id: jest.fn(() => ({})) })),
    forceManyBody: jest.fn(() => ({ strength: jest.fn(() => ({})) })),
    forceCenter: jest.fn(() => ({})),
    drag: jest.fn(() => ({ on: jest.fn(() => ({})) }))
  };
});

const mockData = {
  nodes: [{ id: '1' }, { id: '2' }, { id: '3' }],
  links: [{ source: '1', target: '2' }, { source: '2', target: '3' }],
};

describe('Graph Component', () => {
  test('renders an SVG element', () => {
    const { container } = render(<Graph data={{ nodes: [], links: [] }} onNodeClick={jest.fn()} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  test('creates d3 elements based on node and link data', () => {
    render(<Graph data={mockData} onNodeClick={jest.fn()} />);
    
    const d3Mock = require('d3');
    expect(d3Mock._elements.circles.length).toBe(3);
    expect(d3Mock._elements.lines.length).toBe(2);
  });

  test('calls onNodeClick when a node is clicked', () => {
    const mockOnNodeClick = jest.fn();
    render(<Graph data={mockData} onNodeClick={mockOnNodeClick} />);
    
    const d3Mock = require('d3');
    const firstCircle = d3Mock._elements.circles[0];
    
    if (firstCircle._eventHandlers && firstCircle._eventHandlers.click) {
      firstCircle._eventHandlers.click(null, mockData.nodes[0]);
      expect(mockOnNodeClick).toHaveBeenCalledWith(mockData.nodes[0]);
    } else {
      throw new Error('Click handler not found on circle element');
    }
  });

  test('clears and recreates elements when data changes', () => {
    const initialData = {
      nodes: [{ id: '1' }, { id: '2' }],
      links: [{ source: '1', target: '2' }]
    };
    
    const updatedData = {
      nodes: [{ id: '1' }, { id: '2' }, { id: '3' }],
      links: [{ source: '1', target: '2' }, { source: '2', target: '3' }]
    };
    
    const { rerender } = render(<Graph data={initialData} onNodeClick={jest.fn()} />);
    
    const d3Mock = require('d3');
    expect(d3Mock._elements.circles.length).toBe(2);
    expect(d3Mock._elements.lines.length).toBe(1);
    
    rerender(<Graph data={updatedData} onNodeClick={jest.fn()} />);
    
    expect(d3Mock._elements.circles.length).toBe(3);
    expect(d3Mock._elements.lines.length).toBe(2);
  });

  test('renders with no nodes', () => {
    render(<Graph data={{ nodes: [], links: [] }} onNodeClick={jest.fn()} />);
  });
});