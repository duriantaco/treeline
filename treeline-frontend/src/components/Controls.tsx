import React, { useState } from 'react';

interface ControlsProps {
  onResetZoom: () => void;
  onToggleLayout: () => void;
  onSearchChange: (term: string) => void;
  isHierarchical: boolean;
  onToggleHierarchical: () => void;
}

const Controls: React.FC<ControlsProps> = ({ 
  onResetZoom, 
  onToggleLayout, 
  onSearchChange,
  isHierarchical,
  onToggleHierarchical
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTerm = e.target.value;
    setSearchTerm(newTerm);
    onSearchChange(newTerm);
  };
  
  return (
    <div id="controls">
      <div>
        <input 
          type="text" 
          id="search" 
          placeholder="Search nodes..." 
          value={searchTerm}
          onChange={handleSearchChange}
        />
      </div>
      <div className="controls-buttons">
        <button onClick={onResetZoom}>Reset View</button>
        <button onClick={onToggleLayout}>Toggle Layout</button>
        <button onClick={onToggleHierarchical}>
          {isHierarchical ? 'Force Layout' : 'Hierarchical View'}
        </button>
      </div>
    </div>
  );
};

export default Controls;