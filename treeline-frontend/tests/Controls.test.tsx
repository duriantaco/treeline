import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Controls from '../src/components/Controls';
import '@testing-library/jest-dom';

describe('Controls Component', () => {
  const mockProps = {
    onResetZoom: jest.fn(),
    onToggleLayout: jest.fn(),
    onSearchChange: jest.fn(),
    isHierarchical: false,
    onToggleHierarchical: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders Controls component with input and buttons', () => {
    render(<Controls {...mockProps} />);
    expect(screen.getByPlaceholderText('Search nodes...')).toBeInTheDocument();
    expect(screen.getByText('Reset View')).toBeInTheDocument();
    expect(screen.getByText('Toggle Layout')).toBeInTheDocument();
    expect(screen.getByText('Hierarchical View')).toBeInTheDocument();
  });

  test('updates search term and calls onSearchChange on input change', () => {
    render(<Controls {...mockProps} />);
    const searchInput = screen.getByPlaceholderText('Search nodes...');
    fireEvent.change(searchInput, { target: { value: 'test' } });
    expect(searchInput).toHaveValue('test');
    expect(mockProps.onSearchChange).toHaveBeenCalledWith('test');
  });

  test('calls onResetZoom when Reset View button is clicked', () => {
    render(<Controls {...mockProps} />);
    const resetButton = screen.getByText('Reset View');
    fireEvent.click(resetButton);
    expect(mockProps.onResetZoom).toHaveBeenCalled();
  });

  test('calls onToggleLayout when Toggle Layout button is clicked', () => {
    render(<Controls {...mockProps} />);
    const toggleLayoutButton = screen.getByText('Toggle Layout');
    fireEvent.click(toggleLayoutButton);
    expect(mockProps.onToggleLayout).toHaveBeenCalled();
  });

  test('calls onToggleHierarchical when hierarchical toggle button is clicked', () => {
    render(<Controls {...mockProps} />);
    const toggleHierarchicalButton = screen.getByText('Hierarchical View');
    fireEvent.click(toggleHierarchicalButton);
    expect(mockProps.onToggleHierarchical).toHaveBeenCalled();
  });

  test('displays "Hierarchical View" when isHierarchical is false', () => {
    render(<Controls {...mockProps} />);
    expect(screen.getByText('Hierarchical View')).toBeInTheDocument();
  });

  test('displays "Force Layout" when isHierarchical is true', () => {
    render(<Controls {...mockProps} isHierarchical={true} />);
    expect(screen.getByText('Force Layout')).toBeInTheDocument();
  });

  test('calls onSearchChange with empty string when search input is cleared', () => {
    render(<Controls {...mockProps} />);
    const searchInput = screen.getByPlaceholderText('Search nodes...');
    fireEvent.change(searchInput, { target: { value: 'test' } });
    fireEvent.change(searchInput, { target: { value: '' } });
    expect(searchInput).toHaveValue('');
    expect(mockProps.onSearchChange).toHaveBeenCalledWith('');
  });
});