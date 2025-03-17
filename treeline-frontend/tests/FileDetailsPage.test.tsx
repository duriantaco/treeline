import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import '@testing-library/jest-dom';
import { fireEvent } from '@testing-library/react';
import FileDetailsPage from '../src/page/FileDetailsPage'; 
import { fetchNodeByFilePath } from '../src/services/dataServices';

jest.mock('../src/services/dataServices', () => ({
  fetchNodeByFilePath: jest.fn() as jest.Mock<Promise<any>, [string]>,
}));
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ filePath: 'mockFilePath' }),
  useNavigate: () => jest.fn(),
}));

const mockedFetchNodeByFilePath = fetchNodeByFilePath as jest.MockedFunction<typeof fetchNodeByFilePath>;

describe('FileDetailsPage Component', () => {
  const mockNodeData = {
    node: {
      name: 'mockNode',
      type: 'module',
      docstring: 'Mock docstring',
      structure: [
        { type: 'function', name: 'mockFunction', line: 1 },
        { type: 'class', name: 'MockClass', line: 5 },
      ],
      code_smells: [
        { description: 'Mock issue 1', line: 10 },
        { description: 'Mock issue 2', line: 15 },
      ],
      metrics: {
        complexity: 12,
        cognitive_complexity: 18,
        lines: 200,
        functions: 5,
        classes: 2,
        params: 3,
        nested_depth: 4,
      },
    },
    connections: {
      incoming: [],
      outgoing: [],
    },
    file_content: null,
  };

  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.clearAllMocks();
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  test('displays loading state initially', () => {
    mockedFetchNodeByFilePath.mockReturnValue(new Promise(() => {})); 
    render(
      <MemoryRouter initialEntries={['/file/mockFilePath']}>
        <Routes>
          <Route path="/file/:filePath" element={<FileDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('Loading file details...')).toBeInTheDocument();
  });

  test('displays error message on fetch failure', async () => {
    mockedFetchNodeByFilePath.mockRejectedValue(new Error('Fetch error'));
    render(
      <MemoryRouter initialEntries={['/file/mockFilePath']}>
        <Routes>
          <Route path="/file/:filePath" element={<FileDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Error loading file details')).toBeInTheDocument();
      expect(screen.getByText('Fetch error')).toBeInTheDocument();
    });
    expect(consoleErrorSpy).toHaveBeenCalled();
  });

  test('renders file details correctly on successful fetch', async () => {
    mockedFetchNodeByFilePath.mockResolvedValue(mockNodeData);
    render(
      <MemoryRouter initialEntries={['/file/mockFilePath']}>
        <Routes>
          <Route path="/file/:filePath" element={<FileDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('mockNode')).toBeInTheDocument();
      expect(screen.getByText('module')).toBeInTheDocument();
      expect(screen.getByText('Mock docstring')).toBeInTheDocument();

      expect(screen.getByText('File Structure')).toBeInTheDocument();
      expect(screen.getByText('mockFunction')).toBeInTheDocument();
      expect(screen.getByText('MockClass')).toBeInTheDocument();
      expect(screen.getByText('Line 1')).toBeInTheDocument();
      expect(screen.getByText('Line 5')).toBeInTheDocument();

      expect(screen.getByText('Issues (2)')).toBeInTheDocument();
      expect(screen.getByText('Mock issue 1')).toBeInTheDocument();
      expect(screen.getByText('Mock issue 2')).toBeInTheDocument();
      expect(screen.getByText('Line 10')).toBeInTheDocument();
      expect(screen.getByText('Line 15')).toBeInTheDocument();

      expect(screen.getByText('Summary')).toBeInTheDocument();
      expect(screen.getByText('Complexity')).toBeInTheDocument();
      expect(screen.getByText('12')).toBeInTheDocument();
      expect(screen.getByText('Cognitive Complexity')).toBeInTheDocument();
      expect(screen.getByText('18')).toBeInTheDocument();
      expect(screen.getByText('Lines')).toBeInTheDocument();
      expect(screen.getByText('200')).toBeInTheDocument();

      expect(screen.getByText('Key Metrics')).toBeInTheDocument();
      expect(screen.getByText('Functions')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('Classes')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('Parameters')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('Nesting Depth')).toBeInTheDocument();
      expect(screen.getByText('4')).toBeInTheDocument();

      expect(screen.getByText('2 issues')).toBeInTheDocument();
      expect(screen.getByText('High complexity')).toBeInTheDocument();
    });
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  test('navigates back to visualization on button click', async () => {
    const mockNavigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
    mockedFetchNodeByFilePath.mockResolvedValue(mockNodeData);
    render(
      <MemoryRouter initialEntries={['/file/mockFilePath']}>
        <Routes>
          <Route path="/file/:filePath" element={<FileDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('mockNode')).toBeInTheDocument();
    });
    const backButton = screen.getByText('← Back to Visualization');
    fireEvent.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('handles missing node data gracefully', async () => {
    mockedFetchNodeByFilePath.mockResolvedValue(null);
    render(
      <MemoryRouter initialEntries={['/file/mockFilePath']}>
        <Routes>
          <Route path="/file/:filePath" element={<FileDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Error loading file details')).toBeInTheDocument();
      expect(screen.getByText('Failed to load file details.')).toBeInTheDocument();
    });
    expect(consoleErrorSpy).toHaveBeenCalled();
  });
});