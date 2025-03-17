import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, test, beforeEach, jest } from '@jest/globals';
import ComplexityTimeline from '../src/components/ComplexityTimeline';

// not sure how to fix this stupid d3 sht
jest.mock('d3', () => {
  const createChainable = () => {
    const chainObj = function() { return chainObj; };
    chainObj.domain = jest.fn().mockReturnValue(chainObj);
    chainObj.range = jest.fn().mockReturnValue(chainObj);
    chainObj.nice = jest.fn().mockReturnValue(chainObj);
    chainObj.ticks = jest.fn().mockReturnValue(chainObj);
    chainObj.tickFormat = jest.fn().mockReturnValue(chainObj);
    chainObj.x = jest.fn().mockReturnValue(chainObj);
    chainObj.y = jest.fn().mockReturnValue(chainObj);
    chainObj.curve = jest.fn().mockReturnValue(chainObj);
    return chainObj;
  };

  // Create a chainable selection object for D3 methods
  const createSelectionChain = () => {
    const chain = {};
    
    // Add all the methods that need to be chainable
    const methods = [
      'attr', 'style', 'text', 'append', 'call', 
      'data', 'enter', 'exit', 'remove', 'datum',
      'selectAll', 'select', 'on', 'transition',
      'duration', 'delay', 'ease'
    ];
    
    methods.forEach(method => {
      chain[method] = jest.fn().mockReturnValue(chain);
    });
    
    return chain;
  };

  return {
    select: jest.fn().mockReturnValue(createSelectionChain()),
    selectAll: jest.fn().mockReturnValue(createSelectionChain()),
    scaleLinear: jest.fn().mockReturnValue(createChainable()),
    axisBottom: jest.fn().mockReturnValue(createChainable()),
    axisLeft: jest.fn().mockReturnValue(createChainable()),
    line: jest.fn().mockReturnValue(createChainable()),
    max: jest.fn().mockReturnValue(100),
    curveMonotoneX: 'curveMonotoneX',
  };
});

const mockedD3 = jest.requireMock('d3') as jest.Mocked<typeof import('d3')>;

describe('ComplexityTimeline Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(
      <ComplexityTimeline 
        currentComplexity={20} 
        currentCognitiveComplexity={25} 
      />
    );
    
    expect(screen.getByText(/This chart illustrates the potential reduction/i)).toBeInTheDocument();
  });

  test('d3 select is called', () => {
    render(
      <ComplexityTimeline 
        currentComplexity={20} 
        currentCognitiveComplexity={25} 
      />
    );
    
    expect(mockedD3.select).toHaveBeenCalled();
    expect(mockedD3.scaleLinear).toHaveBeenCalled();
  });
});