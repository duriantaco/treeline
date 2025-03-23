import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { act } from 'react';
import MetricsDashboardPage from '../src/components/MetricsDashboard';
import { 
  fetchDetailedMetrics,
  fetchFileDetailedMetrics,
  fetchComplexityBreakdown,
  fetchIssuesByCategory 
} from '../src/services/dataServices';
import '@testing-library/jest-dom';

jest.mock('../src/services/dataServices', () => ({
  fetchDetailedMetrics: jest.fn(),
  fetchFileDetailedMetrics: jest.fn(),
  fetchComplexityBreakdown: jest.fn(),
  fetchIssuesByCategory: jest.fn()
}));

jest.mock('d3', () => {
  const createMockSelection = () => {
    const mockSelection = {
      selectAll: jest.fn(() => createMockSelection()),
      select: jest.fn(() => createMockSelection()),
      append: jest.fn(() => createMockSelection()),
      attr: jest.fn(() => mockSelection),
      style: jest.fn(() => mockSelection),
      text: jest.fn(() => mockSelection),
      call: jest.fn(() => mockSelection),
      data: jest.fn(() => mockSelection),
      enter: jest.fn(() => mockSelection),
      exit: jest.fn(() => mockSelection),
      remove: jest.fn(() => mockSelection)
    };
    return mockSelection;
  };
  
  const createPieFunction = () => {
    const pieFn = jest.fn().mockReturnValue([
      { value: 10, startAngle: 0, endAngle: Math.PI/2, data: { label: 'category1' } },
      { value: 20, startAngle: Math.PI/2, endAngle: Math.PI, data: { label: 'category2' } }
    ]);
    return Object.assign(pieFn, {
      sort: jest.fn().mockReturnValue(pieFn),
      value: jest.fn().mockReturnValue(pieFn)
    });
  };
  
  return {
    select: jest.fn(() => createMockSelection()),
    selectAll: jest.fn(() => createMockSelection()),
    scaleOrdinal: jest.fn().mockReturnValue({
      domain: jest.fn().mockReturnThis(),
      range: jest.fn().mockReturnThis()
    }),
    scaleLinear: jest.fn().mockReturnValue({
      domain: jest.fn().mockReturnThis(),
      range: jest.fn().mockReturnThis()
    }),
    scaleBand: jest.fn().mockReturnValue({
      domain: jest.fn().mockReturnThis(),
      range: jest.fn().mockReturnThis(),
      padding: jest.fn().mockReturnThis(),
      bandwidth: jest.fn().mockReturnValue(10)
    }),
    pie: jest.fn(() => createPieFunction()),
    arc: jest.fn().mockReturnValue({
      innerRadius: jest.fn().mockReturnThis(),
      outerRadius: jest.fn().mockReturnThis(),
      centroid: jest.fn().mockReturnValue([0, 0])
    }),
    max: jest.fn().mockReturnValue(100),
    axisBottom: jest.fn(),
    axisLeft: jest.fn()
  };
});

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

jest.mock('../src/components/ComplexityTimeline', () => ({
  __esModule: true,
  default: () => <div data-testid="complexity-timeline">Complexity Timeline Mock</div>
}));

jest.mock('../src/components/ImpactAnalysis', () => ({
  __esModule: true,
  default: () => <div data-testid="impact-analysis">Impact Analysis Mock</div>
}));

Object.defineProperty(window, 'location', {
  value: { reload: jest.fn() },
  writable: true
});

describe('MetricsDashboardPage Component', () => {
  test('renders loading state initially', async () => {
    (fetchDetailedMetrics as jest.Mock).mockReturnValue(new Promise(() => {}));
    (fetchComplexityBreakdown as jest.Mock).mockReturnValue(new Promise(() => {}));
    (fetchIssuesByCategory as jest.Mock).mockReturnValue(new Promise(() => {}));

    await act(async () => {
      render(
        <BrowserRouter>
          <MetricsDashboardPage />
        </BrowserRouter>
      );
    });

    expect(screen.getByText('Loading metrics data...')).toBeInTheDocument();
  });
});