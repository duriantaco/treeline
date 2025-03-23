import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import NodeMetrics from '../src/components/NodeMetrics';

describe('NodeMetrics Component', () => {
  test('renders without crashing', () => {
    const metrics = { complexity: 5, lines: 50 };
    render(<NodeMetrics metrics={metrics} />);
    expect(screen.getByText('📊 Detailed Metrics')).toBeInTheDocument();
  });

  test('displays all metrics in the table', () => {
    const metrics = {
      complexity: 5,
      lines: 50,
      functions: 3,
      cognitive_complexity: 10,
    };
    render(<NodeMetrics metrics={metrics} />);
    expect(screen.getByText('Complexity')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Lines')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('Functions')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Cognitive Complexity')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  test('applies warning class to metrics that exceed thresholds', () => {
    const metrics = {
      complexity: 15, // > 10
      cognitive_complexity: 20, // > 15
      lines: 150, // > 100
      params: 6, // > 5
      methods: 25, // > 20
      nested_depth: 5, // > 4
      functions: 3, // no threshold
    };
    render(<NodeMetrics metrics={metrics} />);
    const complexityRow = screen.getByText('Complexity').closest('tr');
    expect(complexityRow).toHaveClass('metric-warning');
    const cogComplexityRow = screen.getByText('Cognitive Complexity').closest('tr');
    expect(cogComplexityRow).toHaveClass('metric-warning');
    const linesRow = screen.getByText('Lines').closest('tr');
    expect(linesRow).toHaveClass('metric-warning');
    const paramsRow = screen.getByText('Params').closest('tr');
    expect(paramsRow).toHaveClass('metric-warning');
    const methodsRow = screen.getByText('Methods').closest('tr');
    expect(methodsRow).toHaveClass('metric-warning');
    const depthRow = screen.getByText('Nested Depth').closest('tr');
    expect(depthRow).toHaveClass('metric-warning');
    const functionsRow = screen.getByText('Functions').closest('tr');
    expect(functionsRow).not.toHaveClass('metric-warning');
  });

  test('does not apply warning class to metrics within normal range', () => {
    const metrics = {
      complexity: 5, // <= 10
      cognitive_complexity: 10, // <= 15
      lines: 50, // <= 100
      params: 3, // <= 5
      methods: 10, // <= 20
      nested_depth: 2, // <= 4
    };
    render(<NodeMetrics metrics={metrics} />);
    const complexityRow = screen.getByText('Complexity').closest('tr');
    expect(complexityRow).not.toHaveClass('metric-warning');
    const cogComplexityRow = screen.getByText('Cognitive Complexity').closest('tr');
    expect(cogComplexityRow).not.toHaveClass('metric-warning');
    const linesRow = screen.getByText('Lines').closest('tr');
    expect(linesRow).not.toHaveClass('metric-warning');
    const paramsRow = screen.getByText('Params').closest('tr');
    expect(paramsRow).not.toHaveClass('metric-warning');
    const methodsRow = screen.getByText('Methods').closest('tr');
    expect(methodsRow).not.toHaveClass('metric-warning');
    const depthRow = screen.getByText('Nested Depth').closest('tr');
    expect(depthRow).not.toHaveClass('metric-warning');
  });

  test('correctly formats metric keys', () => {
    const metrics = {
      cognitive_complexity: 10,
      nested_depth: 3,
    };
    render(<NodeMetrics metrics={metrics} />);
    expect(screen.getByText('Cognitive Complexity')).toBeInTheDocument();
    expect(screen.getByText('Nested Depth')).toBeInTheDocument();
  });

  test('ignores metrics with keys starting with underscore', () => {
    const metrics = {
      _internal: 'hidden',
      complexity: 5,
      _private_data: 42,
    };
    render(<NodeMetrics metrics={metrics} />);
    expect(screen.queryByText('_internal')).not.toBeInTheDocument();
    expect(screen.queryByText('hidden')).not.toBeInTheDocument();
    expect(screen.getByText('Complexity')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.queryByText('_private_data')).not.toBeInTheDocument();
    expect(screen.queryByText('42')).not.toBeInTheDocument();
  });

  test('handles empty metrics object', () => {
    render(<NodeMetrics metrics={{}} />);
    const tableRows = screen.queryAllByRole('row');
    expect(tableRows.length).toBe(0);
  });

  test('handles non-numeric metric values', () => {
    const metrics = {
      complexity: 'N/A',
      lines: 50,
      methods: 'unknown',
    };
    render(<NodeMetrics metrics={metrics} />);
    expect(screen.getByText('Complexity')).toBeInTheDocument();
    expect(screen.getByText('N/A')).toBeInTheDocument();
    const complexityRow = screen.getByText('Complexity').closest('tr');
    expect(complexityRow).not.toHaveClass('metric-warning');
    expect(screen.getByText('Lines')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('Methods')).toBeInTheDocument();
    expect(screen.getByText('unknown')).toBeInTheDocument();
    const methodsRow = screen.getByText('Methods').closest('tr');
    expect(methodsRow).not.toHaveClass('metric-warning');
  });
});