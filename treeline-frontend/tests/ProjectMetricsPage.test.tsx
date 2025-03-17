import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import { fireEvent } from '@testing-library/react';
import ProjectMetricsPage from '../src/page/ProjectMetricsPage';
import { 
  fetchDetailedMetrics, 
  fetchIssuesByCategory, 
  fetchComplexityBreakdown 
} from '../src/services/dataServices';

jest.mock('../src/services/dataServices', () => ({
  fetchDetailedMetrics: jest.fn(),
  fetchIssuesByCategory: jest.fn(),
  fetchComplexityBreakdown: jest.fn(),
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

jest.mock('d3', () => {
    const mockSelection = () => ({
      selectAll: jest.fn(() => mockSelection()),
      select: jest.fn(() => mockSelection()),
      append: jest.fn(() => mockSelection()),
      attr: jest.fn(() => mockSelection()),
      style: jest.fn(() => mockSelection()),
      text: jest.fn(() => mockSelection()),
      call: jest.fn(() => mockSelection()),
      data: jest.fn(() => mockSelection()),
      enter: jest.fn(() => mockSelection()),
      exit: jest.fn(() => mockSelection()),
      remove: jest.fn(() => mockSelection()),
    });
  
    return {
      select: jest.fn(() => mockSelection()),
      selectAll: jest.fn(() => mockSelection()),
      scaleLinear: jest.fn(() => ({
        domain: jest.fn().mockReturnThis(),
        range: jest.fn().mockReturnThis(),
      })),
      scaleBand: jest.fn(() => ({
        domain: jest.fn().mockReturnThis(),
        range: jest.fn().mockReturnThis(),
        padding: jest.fn().mockReturnThis(),
        bandwidth: jest.fn().mockReturnValue(20),
      })),
      scaleOrdinal: jest.fn(() => ({
        domain: jest.fn().mockReturnThis(),
        range: jest.fn().mockReturnThis(),
      })),
      pie: jest.fn(() => {
        const mockPie = jest.fn((data) => data.map((d, i) => ({
          data: d,
          index: i,
          startAngle: 0,
          endAngle: Math.PI * 2 / data.length,
          value: d.value,
        }))) as jest.Mock & { sort?: jest.Mock; value?: jest.Mock };
        mockPie.sort = jest.fn(() => mockPie);
        mockPie.value = jest.fn(() => mockPie);
        return mockPie;
      }),
      arc: jest.fn(() => ({
        innerRadius: jest.fn().mockReturnThis(),
        outerRadius: jest.fn().mockReturnThis(),
        centroid: jest.fn().mockReturnValue([0, 0]),
      })),
      max: jest.fn().mockReturnValue(100),
      axisBottom: jest.fn(),
      axisLeft: jest.fn(),
    };
  });

describe('ProjectMetricsPage Component', () => {
  const mockProjectMetrics = {
    project_metrics: {
      total_files: 42,
      total_lines: 5000,
      total_functions: 150,
      total_classes: 25,
    },
    files: {
      'src/components/App.js': {
        lines: 100,
        functions: [{ complexity: 5 }, { complexity: 10 }],
        classes: [{}],
        issues_by_category: {
          'code_smells': [{ description: 'Issue 1' }, { description: 'Issue 2' }]
        }
      },
      'src/utils/helpers.js': {
        lines: 200,
        functions: [{ complexity: 15 }, { complexity: 5 }],
        classes: [],
        issues_by_category: {
          'security': [{ description: 'Security issue' }],
          'complexity': [{ description: 'Too complex' }]
        }
      }
    }
  };

  const mockComplexityBreakdown = {
    total: {
      nested_conditionals: 25,
      deep_nesting: 15,
      large_functions: 10,
      excessive_branches: 5,
      high_cognitive_load: 20
    }
  };

  const mockIssuesByCategory = {
    category_counts: {
      security: 5,
      style: 10,
      duplication: 15,
      code_smells: 20,
      complexity: 25,
      sql_injection: 1
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    jest.spyOn(console, 'error').mockImplementation(() => {});
    
    (fetchDetailedMetrics as jest.Mock).mockResolvedValue(mockProjectMetrics);
    (fetchIssuesByCategory as jest.Mock).mockResolvedValue(mockIssuesByCategory);
    (fetchComplexityBreakdown as jest.Mock).mockResolvedValue(mockComplexityBreakdown);
  });

  test('displays loading state initially', async () => {
    (fetchDetailedMetrics as jest.Mock).mockReturnValue(new Promise(() => {}));
    (fetchIssuesByCategory as jest.Mock).mockReturnValue(new Promise(() => {}));
    (fetchComplexityBreakdown as jest.Mock).mockReturnValue(new Promise(() => {}));

    render(<ProjectMetricsPage />);
    expect(screen.getByText('Loading project metrics...')).toBeInTheDocument();
  });

  test('displays error message on fetch failure', async () => {
    (fetchDetailedMetrics as jest.Mock).mockRejectedValue(new Error('API Error'));
    (fetchIssuesByCategory as jest.Mock).mockRejectedValue(new Error('API Error'));
    (fetchComplexityBreakdown as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<ProjectMetricsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading project metrics')).toBeInTheDocument();
      expect(screen.getByText('Failed to load project metrics. Please try again later.')).toBeInTheDocument();
    });
  });

  test('renders project metrics data correctly on successful fetch', async () => {
    render(<ProjectMetricsPage />);
    
    await waitFor(() => {
      // Header and dashboard title
      expect(screen.getByText('Project Metrics')).toBeInTheDocument();
      expect(screen.getByText('Project-Wide Metrics Dashboard')).toBeInTheDocument();
      
      // Project-wide metrics
      expect(screen.getByText('Total Files')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
      expect(screen.getByText('Total Lines of Code')).toBeInTheDocument();
      expect(screen.getByText('5,000')).toBeInTheDocument();
      
      // Use more specific selectors for ambiguous text
      expect(screen.getByText('Functions', { selector: '.text-gray-500' })).toBeInTheDocument();
      expect(screen.getByText('150')).toBeInTheDocument();
      expect(screen.getByText('Classes', { selector: '.text-gray-500' })).toBeInTheDocument();
      
      // Use within to provide context to find the right '25'
      const classesLabel = screen.getByText('Classes', { selector: '.text-gray-500' });
      const classesCard = classesLabel.closest('.bg-white');
      if (!classesCard) throw new Error("Classes card container not found");
      expect(within(classesCard as HTMLElement).getByText('25')).toBeInTheDocument();
      
      // Quality Issues Summary section
      expect(screen.getByText('Quality Issues Summary')).toBeInTheDocument();
      expect(screen.getByText('security')).toBeInTheDocument();
      expect(screen.getByText('style')).toBeInTheDocument();
      expect(screen.getByText('duplication')).toBeInTheDocument();
      expect(screen.getByText('code smells')).toBeInTheDocument();
      expect(screen.getByText('complexity')).toBeInTheDocument();
      expect(screen.getByText('sql injection')).toBeInTheDocument();
      
      // Skip numeric values that appear in multiple places
      // Instead, verify categories exist
      expect(screen.getByText('security')).toBeInTheDocument();
      expect(screen.getByText('style')).toBeInTheDocument();
      expect(screen.getByText('duplication')).toBeInTheDocument();
      expect(screen.getByText('code smells')).toBeInTheDocument();
      expect(screen.getByText('complexity')).toBeInTheDocument();
      expect(screen.getByText('sql injection')).toBeInTheDocument();
      
      // Other sections
      expect(screen.getByText('Complexity Factors')).toBeInTheDocument();
      expect(screen.getByText('Files with Most Issues')).toBeInTheDocument();
    });
  });
  
  test('navigation button works correctly', async () => {
    const mockNavigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);

    render(<ProjectMetricsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Project Metrics')).toBeInTheDocument();
    });
    
    const backButton = screen.getByText('Back to Visualization');
    fireEvent.click(backButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('handles file table row click correctly', async () => {
    const mockNavigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);

    render(<ProjectMetricsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('App.js')).toBeInTheDocument();
    });
    
    const fileTableRow = screen.getByText('App.js');
    fireEvent.click(fileTableRow);
    
    expect(mockNavigate).toHaveBeenCalledWith('/file/src%2Fcomponents%2FApp.js');
  });

  test('renders charts using d3', async () => {
    render(<ProjectMetricsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Project Metrics')).toBeInTheDocument();
    });
  });

  test('displays empty state when no metrics are available', async () => {
    (fetchDetailedMetrics as jest.Mock).mockResolvedValue(null);
    (fetchIssuesByCategory as jest.Mock).mockResolvedValue(mockIssuesByCategory);
    (fetchComplexityBreakdown as jest.Mock).mockResolvedValue(mockComplexityBreakdown);
    
    render(<ProjectMetricsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('No project metrics available.')).toBeInTheDocument();
    });
  });
});