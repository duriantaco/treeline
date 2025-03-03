import { GraphData } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export async function fetchGraphData(): Promise<GraphData> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph-data`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching graph data:', error);
    throw error;
  }
}

export async function fetchNodeData(nodeId: string): Promise<any> {
  try {
    console.log(`Fetching data for node: ${nodeId}`);
    const response = await fetch(`${API_BASE_URL}/api/node/${nodeId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        const errorData = await response.json();
        throw new Error(`Node not found: ${errorData.detail || 'The requested node does not exist'}`);
      }
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data for node ${nodeId}:`, error);
    throw error;
  }
}