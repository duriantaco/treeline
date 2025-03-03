import React from 'react';

const Legend: React.FC = () => {
  return (
    <div className="legend p-4 bg-white shadow-md rounded-lg">
      <h3 className="text-lg font-bold mb-2">Legend</h3>
      <h3 className="text-red-500">Legend</h3>
      <h3 className="text-red-500">Legend</h3>

      <div className="space-y-2">
        <div className="flex items-center">
          <div className="legend-color module-color mr-2"></div>
          <span>Module</span>
        </div>
        <div className="flex items-center">
          <div className="legend-color entry-point-color mr-2"></div>
          <span>Entry Point</span>
        </div>
        <div className="flex items-center">
          <div className="legend-color class-color mr-2"></div>
          <span>Class</span>
        </div>
        <div className="flex items-center">
          <div className="legend-color function-color mr-2"></div>
          <span>Function</span>
        </div>
        <div className="mt-4 space-y-2">
          <div className="flex items-center">
            <div className="legend-line imports-line mr-2"></div>
            <span>Imports</span>
          </div>
          <div className="flex items-center">
            <div className="legend-line contains-line mr-2"></div>
            <span>Contains</span>
          </div>
          <div className="flex items-center">
            <div className="legend-line calls-line mr-2"></div>
            <span>Calls</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Legend;