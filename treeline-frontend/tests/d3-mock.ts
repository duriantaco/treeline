const mockSelect = function() {
    return {
      selectAll: function() {
        return {
          remove: function() {}
        };
      },
      attr: function() { return this; },
      append: function() { return this; },
      call: function() { return this; },
      style: function() { return this; },
      text: function() { return this; },
      datum: function() { return this; },
      data: function() { return this; },
      enter: function() { return this; }
    };
  };
  
  const mockD3 = {
    select: mockSelect,
    scaleLinear: function() { return function() {}; },
    axisBottom: function() { return function() {}; },
    axisLeft: function() { return function() {}; },
    line: function() { return function() {}; },
    max: function() { return 100; },
    curveMonotoneX: 'curveMonotoneX'
  };
  
  export default mockD3;