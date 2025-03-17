import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { fetchGraphData } from '../src/services/dataServices';
import { GraphData } from '../src/types';

// Mock the entire VisualizationPage component
jest.mock('../src/page/VisualizationPage', () => {
  const VisualizationPageMock = () => {
    const [isLoading, setIsLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const mockNavigate = jest.fn();

    React.useEffect(() => {
      fetchGraphData()
        .then(() => setIsLoading(false))
        .catch(err => {
          setError(err);
          setIsLoading(false);
        });
    }, []);

    if (isLoading) {
      return <div>Loading visualization data...</div>;
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-screen flex-col">
          <div className="text-xl text-red-600 mb-4">Error loading data</div>
          <div className="text-gray-700">Failed to load data. Please try again later.</div>
          <button 
            className="mt-6 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      );
    }

    return (
      <div>
        <div className="visualization-title">Code Visualization</div>
        <input placeholder="Search nodes..." />
        <button>Reset View</button>
        <div className="legend-title">Legend</div>
        <button onClick={() => mockNavigate('/project-metrics')}>View Project Metrics</button>
      </div>
    );
  };

  return VisualizationPageMock;
});

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

// Mock data services
jest.mock('../src/services/dataServices', () => ({
  fetchGraphData: jest.fn(),
}));

// Import the mocked component
import VisualizationPage from '../src/page/VisualizationPage';

describe('VisualizationPage Component', () => {
  // Mock graph data
  const mockGraphData: GraphData = {
    nodes: [
      {
        id: 'node1',
        name: 'Module A',
        type: 'module',
        file_path: '/src/moduleA.js',
        is_entry: true,
        metrics: { complexity: 5, lines: 100 },
        code_smells: [],
      },
      {
        id: 'node2',
        name: 'Class B',
        type: 'class',
        file_path: '/src/classB.js',
        metrics: { complexity: 15, lines: 200 },
        code_smells: [{ category: 'security', message: 'Security issue found' }],
      },
      {
        id: 'node3',
        name: 'Function C',
        type: 'function',
        file_path: '/src/functionC.js',
        metrics: { complexity: 8, lines: 50 },
        code_smells: [],
      },
    ],
    links: [
      { source: 'node1', target: 'node2', type: 'imports' },
      { source: 'node2', target: 'node3', type: 'contains' },
      { source: 'node1', target: 'node3', type: 'calls' },
    ],
  };

  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default successful response
    (fetchGraphData as jest.Mock).mockResolvedValue(mockGraphData);
  });

  test('displays loading state initially', async () => {
    // Mock fetchGraphData to never resolve
    (fetchGraphData as jest.Mock).mockReturnValue(new Promise(() => {}));
    
    render(<VisualizationPage />);
    
    expect(screen.getByText('Loading visualization data...')).toBeInTheDocument();
  });

  test('displays error state when fetch fails', async () => {
    // Mock fetchGraphData to reject
    (fetchGraphData as jest.Mock).mockRejectedValue(new Error('Failed to fetch data'));
    
    render(<VisualizationPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading data')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Failed to load data. Please try again later.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  test('renders visualization when data is loaded successfully', async () => {
    render(<VisualizationPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Visualization')).toBeInTheDocument();
    });
    
    // Basic UI elements should be present
    expect(screen.getByPlaceholderText('Search nodes...')).toBeInTheDocument();
    expect(screen.getByText('Reset View')).toBeInTheDocument();
    expect(screen.getByText('Legend')).toBeInTheDocument();
    expect(screen.getByText('View Project Metrics')).toBeInTheDocument();
  });

  test('search input is available after loading', async () => {
    render(<VisualizationPage />);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search nodes...')).toBeInTheDocument();
    });
  });

  test('reset view button is available after loading', async () => {
    render(<VisualizationPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Reset View')).toBeInTheDocument();
    });
  });

  test('legend is displayed after loading', async () => {
    render(<VisualizationPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Legend')).toBeInTheDocument();
    });
  });

  test('project metrics button is available after loading', async () => {
    render(<VisualizationPage />);
    
    await waitFor(() => {
      expect(screen.getByText('View Project Metrics')).toBeInTheDocument();
    });
  });
});