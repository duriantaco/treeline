import ast
from pathlib import Path
from collections import defaultdict
import json

class ModuleDependencyAnalyzer:
    """Analyzes module-level dependencies and generates summary reports."""
    
    def __init__(self):
        self.module_imports = defaultdict(set)
        self.module_metrics = defaultdict(dict)
        self.complex_functions = []
        self.function_locations = defaultdict(dict)   
        self.function_calls = defaultdict(list)       
        self.class_info = defaultdict(dict)      
        self.html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Structure Visualization</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
            <style>
                body { 
                    margin: 0; 
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: #f8f9fa;
                }
                .node { 
                    cursor: pointer; 
                }
                .node circle { 
                    fill: #fff; 
                    stroke-width: 2px; 
                    transition: all 0.3s;
                }
                .node:hover circle {
                    filter: brightness(0.95);
                }
                .node text { 
                    font: 12px 'Segoe UI', sans-serif;
                    font-weight: 500;
                }
                .link { 
                    stroke-width: 1.5px;
                    stroke-dasharray: 4;
                    opacity: 0.7;
                }
                .link-imports {
                    stroke: #7c3aed; /* purple */
                }
                .link-contains {
                    stroke: #059669; /* green */
                }
                .link-calls {
                    stroke: #ea580c; /* orange */
                }
                .tooltip { 
                    position: absolute; 
                    padding: 12px;
                    background: white;
                    border: none;
                    border-radius: 8px;
                    pointer-events: none;
                    font-size: 14px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    max-width: 300px;
                }
                #controls {
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    background: white;
                    padding: 16px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    z-index: 1000;
                }
                #search {
                    width: 250px;
                    padding: 8px 12px;
                    margin-bottom: 12px;
                    border: 1px solid #e5e7eb;
                    border-radius: 6px;
                    font-size: 14px;
                }
                button {
                    background: #1d4ed8;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-right: 8px;
                    transition: background 0.3s;
                }
                button:hover {
                    background: #1e40af;
                }
                .legend {
                    position: fixed;
                    bottom: 20px;
                    left: 20px;
                    background: white;
                    padding: 16px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }
                .legend-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                    font-size: 14px;
                }
                .legend-color {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    margin-right: 8px;
                }
                .node-module circle { stroke: #0284c7; }
                .node-class circle { stroke: #0891b2; }
                .node-function circle { stroke: #0d9488; }
            </style>
        </head>
        <body>
            <div id="controls">
                <input type="text" id="search" placeholder="Search nodes...">
                <button onclick="resetZoom()">Reset View</button>
                <button onclick="toggleLayout()">Toggle Layout</button>
            </div>
            <div class="legend">
                <h3 style="margin-top: 0; margin-bottom: 12px;">Legend</h3>
                <div class="legend-item">
                    <div class="legend-color" style="background: #0284c7;"></div>
                    <span>Module</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #0891b2;"></div>
                    <span>Class</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #0d9488;"></div>
                    <span>Function</span>
                </div>
                <div style="margin-top: 16px; border-top: 1px solid #e5e7eb; padding-top: 12px;">
                    <div class="legend-item">
                        <div style="width: 40px; height: 2px; background: #7c3aed; margin-right: 8px;"></div>
                        <span>Imports</span>
                    </div>
                    <div class="legend-item">
                        <div style="width: 40px; height: 2px; background: #059669; margin-right: 8px;"></div>
                        <span>Contains</span>
                    </div>
                    <div class="legend-item">
                        <div style="width: 40px; height: 2px; background: #ea580c; margin-right: 8px;"></div>
                        <span>Calls</span>
                    </div>
                </div>
            </div>
            <svg id="visualization"></svg>
            <script>
                const data = GRAPH_DATA_PLACEHOLDER;

                let width = window.innerWidth;
                let height = window.innerHeight;
                
                const svg = d3.select("#visualization")
                    .attr("width", width)
                    .attr("height", height);

                // Define arrow markers for different link types
                svg.append("defs").selectAll("marker")
                    .data(["imports", "contains", "calls"])
                    .join("marker")
                    .attr("id", d => `arrow-${d}`)
                    .attr("viewBox", "0 -5 10 10")
                    .attr("refX", 15)
                    .attr("refY", 0)
                    .attr("markerWidth", 6)
                    .attr("markerHeight", 6)
                    .attr("orient", "auto")
                    .append("path")
                    .attr("fill", d => d === "imports" ? "#7c3aed" : d === "contains" ? "#059669" : "#ea580c")
                    .attr("d", "M0,-5L10,0L0,5");

                const g = svg.append("g");

                const zoom = d3.zoom()
                    .scaleExtent([0.1, 4])
                    .on("zoom", (event) => {
                        g.attr("transform", event.transform);
                    });

                svg.call(zoom);

                function resetZoom() {
                    svg.transition().duration(750).call(
                        zoom.transform,
                        d3.zoomIdentity
                    );
                }

                let isRadial = false;
                const simulation = d3.forceSimulation()
                    .force("link", d3.forceLink().id(d => d.id).distance(150))
                    .force("charge", d3.forceManyBody().strength(-1000))
                    .force("x", d3.forceX(width / 2).strength(0.1))
                    .force("y", d3.forceY(height / 2).strength(0.1))
                    .force("collision", d3.forceCollide().radius(50));

                const tooltip = d3.select("body").append("div")
                    .attr("class", "tooltip")
                    .style("opacity", 0);

                const link = g.append("g")
                    .selectAll("path")
                    .data(data.links)
                    .join("path")
                    .attr("class", d => `link link-${d.type}`)
                    .attr("marker-end", d => `url(#arrow-${d.type})`);

                const node = g.append("g")
                    .selectAll(".node")
                    .data(data.nodes)
                    .join("g")
                    .attr("class", d => `node node-${d.type}`)
                    .call(drag(simulation));

                node.append("circle")
                    .attr("r", d => getNodeSize(d))
                    .style("fill", "#fff");

                node.append("text")
                    .attr("dy", ".35em")
                    .attr("x", d => getNodeSize(d) + 5)
                    .text(d => d.name)
                    .style("fill", "#333");

                // Add hover effects
                node.on("mouseover", function(event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    
                    let connections = data.links.filter(l => 
                        l.source.id === d.id || l.target.id === d.id
                    );
                    
                    let tooltipContent = `<strong>${d.name}</strong><br>Type: ${d.type}<br><br>`;
                    if (connections.length > 0) {
                        tooltipContent += "Connections:<br>";
                        connections.forEach(c => {
                            if (c.source.id === d.id) {
                                tooltipContent += `→ ${c.target.name} (${c.type})<br>`;
                            } else {
                                tooltipContent += `← ${c.source.name} (${c.type})<br>`;
                            }
                        });
                    }
                    
                    tooltip.html(tooltipContent)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                        
                    // Highlight connected nodes
                    node.style("opacity", n => 
                        n.id === d.id || 
                        connections.some(c => c.source.id === n.id || c.target.id === n.id) ? 1 : 0.1
                    );
                    link.style("opacity", l => 
                        l.source.id === d.id || l.target.id === d.id ? 1 : 0.1
                    );
                })
                .on("mouseout", function() {
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                    node.style("opacity", 1);
                    link.style("opacity", 0.7);
                });

                simulation
                    .nodes(data.nodes)
                    .on("tick", ticked);

                simulation.force("link")
                    .links(data.links);

                function ticked() {
                    link.attr("d", linkArc);
                    node.attr("transform", d => `translate(${d.x},${d.y})`);
                }

                function linkArc(d) {
                    return `M${d.source.x},${d.source.y}L${d.target.x},${d.target.y}`;
                }

                function getNodeSize(node) {
                    switch(node.type) {
                        case 'module': return 12;
                        case 'class': return 10;
                        default: return 8;
                    }
                }

                function drag(simulation) {
                    function dragstarted(event) {
                        if (!event.active) simulation.alphaTarget(0.3).restart();
                        event.subject.fx = event.subject.x;
                        event.subject.fy = event.subject.y;
                    }

                    function dragged(event) {
                        event.subject.fx = event.x;
                        event.subject.fy = event.y;
                    }

                    function dragended(event) {
                        if (!event.active) simulation.alphaTarget(0);
                        event.subject.fx = null;
                        event.subject.fy = null;
                    }

                    return d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended);
                }

                function toggleLayout() {
                    isRadial = !isRadial;
                    if (isRadial) {
                        simulation
                            .force("x", null)
                            .force("y", null)
                            .force("r", d3.forceRadial(250, width / 2, height / 2))
                            .force("charge", d3.forceManyBody().strength(-100));
                    } else {
                        simulation
                            .force("r", null)
                            .force("x", d3.forceX(width / 2).strength(0.1))
                            .force("y", d3.forceY(height / 2).strength(0.1))
                            .force("charge", d3.forceManyBody().strength(-1000));
                    }
                    simulation.alpha(1).restart();
                }

                // Search functionality with highlighting
                d3.select("#search").on("input", function() {
                    const term = this.value.toLowerCase();
                    if (term === "") {
                        node.style("opacity", 1);
                        link.style("opacity", 0.7);
                        return;
                    }
                    
                    const matchedNodes = new Set();
                    node.each(function(d) {
                        if (d.name.toLowerCase().includes(term)) {
                            matchedNodes.add(d.id);
                            // Also add connected nodes
                            data.links.forEach(l => {
                                if (l.source.id === d.id) matchedNodes.add(l.target.id);
                                if (l.target.id === d.id) matchedNodes.add(l.source.id);
                            });
                        }
                    });
                    
                    node.style("opacity", d => matchedNodes.has(d.id) ? 1 : 0.1);
                    link.style("opacity", d =>
                        matchedNodes.has(d.source.id) && matchedNodes.has(d.target.id) ? 0.7 : 0.1
                    );
                });

                // Window resize handler
                window.addEventListener("resize", () => {
                    width = window.innerWidth;
                    height = window.innerHeight;
                    svg.attr("width", width).attr("height", height);
                    simulation.force("center", d3.forceCenter(width / 2, height / 2));
                    simulation.alpha(1).restart();
                });
            </script>
        </body>
        </html>
        '''
    
    def analyze_directory(self, directory: Path):
        """Analyze all Python files in directory."""
        for file_path in directory.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                module_name = str(file_path.relative_to(directory)).replace('/', '.').replace('.py', '')
                self._analyze_module(tree, module_name, str(file_path))
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

    def _analyze_module(self, tree: ast.AST, module_name: str, file_path: str):
        """Analyze a single module's contents and relationships."""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                setattr(child, 'parent', parent)
                
        self._analyze_imports(tree, module_name)
        self._collect_metrics(tree, module_name)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                parent = getattr(node, 'parent', None)
                if isinstance(parent, ast.Module):
                    self.function_locations[node.name] = {
                        'module': module_name,
                        'file': file_path,
                        'line': node.lineno
                    }
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            self.function_calls[child.func.id].append({
                                'from_module': module_name,
                                'from_function': node.name,
                                'line': child.lineno
                            })
            
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'module': module_name,
                    'file': file_path,
                    'line': node.lineno,
                    'methods': {}
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = f"{node.name}.{item.name}"
                        class_info['methods'][item.name] = {
                            'line': item.lineno,
                            'calls': []
                        }
                        for child in ast.walk(item):
                            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                                class_info['methods'][item.name]['calls'].append(child.func.id)
                
                self.class_info[module_name][node.name] = class_info
    
    def _analyze_imports(self, tree: ast.AST, module_name: str):
        """Collect import information from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.module_imports[module_name].add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.module_imports[module_name].add(node.module)
    
    def _collect_metrics(self, tree: ast.AST, module_name: str):
        """Collect code metrics for the module."""
        functions = []
        classes = []
        total_complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 10:  # Threshold for complex functions
                    self.complex_functions.append((module_name, node.name, complexity))
                total_complexity += complexity
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        self.module_metrics[module_name] = {
            'functions': len(functions),
            'classes': len(classes),
            'complexity': total_complexity
        }
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def generate_module_overview_diagram(self) -> str:
        """Generate a Mermaid diagram showing modules and their relationships."""
        mermaid_lines = ['graph TD\n']  
        mermaid_lines.append('    %% Styling')
        mermaid_lines.append('    classDef modNode fill:#b7e2d8,stroke:#333,stroke-width:2px\n')  
        
        added_nodes = set()
        for module in self.module_imports:
            clean_module = module.replace('.', '_')
            if clean_module not in added_nodes:
                mermaid_lines.append(f'    {clean_module}["{module}"]:::modNode')
                added_nodes.add(clean_module)
        
        mermaid_lines.append('')
        
        for module, imports in self.module_imports.items():
            clean_module = module.replace('.', '_')
            for imp in imports:
                if imp in self.module_imports:
                    clean_imp = imp.replace('.', '_')
                    mermaid_lines.append(f'    {clean_module} --> {clean_imp}')
        
        return '\n'.join(mermaid_lines)

    def generate_module_detail_diagram(self, module: str) -> str:
        """Generate a Mermaid diagram showing functions and classes in a module."""
        mermaid_lines = ['graph TD\n']  # Added newline
        mermaid_lines.append('    %% Styling')
        mermaid_lines.append('    classDef fnNode fill:#e4d1d1,stroke:#333')
        mermaid_lines.append('    classDef clsNode fill:#d1e0e4,stroke:#333\n')  # Added newline
        
        clean_module = module.replace('.', '_')
        
        mermaid_lines.append(f'    subgraph {clean_module}["{module}"]')
        mermaid_lines.append('        direction TB')  
        added_nodes = set()
        
        if module in self.class_info:
            for class_name, info in self.class_info[module].items():
                clean_class = f"{clean_module}_{class_name}"
                if clean_class not in added_nodes:
                    mermaid_lines.append(f'        {clean_class}["📦 {class_name}"]:::clsNode')
                    added_nodes.add(clean_class)
                
                for method_name in info['methods']:
                    clean_method = f"{clean_class}_{method_name}"
                    if clean_method not in added_nodes:
                        mermaid_lines.append(f'        {clean_method}["⚡ {method_name}"]:::fnNode')
                        mermaid_lines.append(f'        {clean_class} --> {clean_method}')
                        added_nodes.add(clean_method)
        
        for func_name, location in self.function_locations.items():
            if location['module'] == module and 'in_class' not in location:
                clean_func = f"{clean_module}_{func_name}"
                if clean_func not in added_nodes:
                    mermaid_lines.append(f'        {clean_func}["⚡ {func_name}"]:::fnNode')
                    added_nodes.add(clean_func)
        
        mermaid_lines.append('    end\n')  
        
        for func_name, calls in self.function_calls.items():
            if func_name in self.function_locations and self.function_locations[func_name]['module'] == module:
                to_func = f"{clean_module}_{func_name}"
                for call in calls:
                    if call['from_module'] == module:
                        from_func = f"{clean_module}_{call['from_function']}"
                        if from_func in added_nodes and to_func in added_nodes:
                            mermaid_lines.append(f'    {from_func} -.->|calls| {to_func}')
        
        return '\n'.join(mermaid_lines)

    def generate_mermaid_graphs(self) -> str:
        """Generate a markdown report with multiple focused Mermaid graphs."""
        sections = []
        
        sections.append("```mermaid")
        sections.append(self.generate_module_overview_diagram())
        sections.append("```\n")
        
        for module in sorted(self.module_imports.keys()):
            if module.startswith('treeline.'):  
                sections.append(f"### {module}\n")
                sections.append("```mermaid")
                sections.append(self.generate_module_detail_diagram(module))
                sections.append("```\n")
        
        return '\n'.join(sections)

    ## for the entire graph
    # def generate_mermaid_graph(self) -> str:
    #     """Generate detailed Mermaid graph showing module, function, and class relationships."""
    #     mermaid_lines = ['graph TD']
    #     mermaid_lines.append('    %% Styling')
    #     mermaid_lines.append('    classDef modNode fill:#b7e2d8,stroke:#333,stroke-width:2px')
    #     mermaid_lines.append('    classDef fnNode fill:#e4d1d1,stroke:#333')
    #     mermaid_lines.append('    classDef clsNode fill:#d1e0e4,stroke:#333')
        
    #     added_nodes = set()
    #     node_id = 0  
    #     node_map = {}  
        
    #     def get_node_id(name: str) -> str:
    #         nonlocal node_id
    #         if name not in node_map:
    #             node_map[name] = f"n{node_id}"
    #             node_id += 1
    #         return node_map[name]
        
    #     for module in self.module_imports:
    #         clean_module = get_node_id(module)
    #         if clean_module not in added_nodes:
    #             mermaid_lines.append(f'    {clean_module}["{module}"]:::modNode')
    #             added_nodes.add(clean_module)
            
    #         for func_name, location in self.function_locations.items():
    #             if location['module'] == module:
    #                 clean_func = get_node_id(f"{module}_{func_name}")
    #                 if clean_func not in added_nodes:
    #                     mermaid_lines.append(f'    {clean_func}["⚡ {func_name}"]:::fnNode')
    #                     mermaid_lines.append(f'    {clean_module} --> {clean_func}')
    #                     added_nodes.add(clean_func)
            
    #         if module in self.class_info:
    #             for class_name, info in self.class_info[module].items():
    #                 clean_class = get_node_id(f"{module}_{class_name}")
    #                 if clean_class not in added_nodes:
    #                     mermaid_lines.append(f'    {clean_class}["📦 {class_name}"]:::clsNode')
    #                     mermaid_lines.append(f'    {clean_module} --> {clean_class}')
    #                     added_nodes.add(clean_class)
                    
    #                 for method_name in info['methods']:
    #                     clean_method = get_node_id(f"{module}_{class_name}_{method_name}")
    #                     if clean_method not in added_nodes:
    #                         mermaid_lines.append(f'    {clean_method}["⚡ {method_name}"]:::fnNode')
    #                         mermaid_lines.append(f'    {clean_class} --> {clean_method}')
    #                         added_nodes.add(clean_method)
        
    #     for func_name, calls in self.function_calls.items():
    #         for call in calls:
    #             if func_name in self.function_locations:
    #                 from_module = call['from_module']
    #                 to_module = self.function_locations[func_name]['module']
    #                 from_func = get_node_id(f"{from_module}_{call['from_function']}")
    #                 to_func = get_node_id(f"{to_module}_{func_name}")
                    
    #                 if from_func in node_map.values() and to_func in node_map.values():
    #                     mermaid_lines.append(f'    {from_func} -.->|calls| {to_func}')
        
    #     for module, imports in self.module_imports.items():
    #         clean_module = get_node_id(module)
    #         for imp in imports:
    #             clean_imp = get_node_id(imp)
    #             if clean_module in node_map.values() and clean_imp in node_map.values():
    #                 mermaid_lines.append(f'    {clean_module} -->|imports| {clean_imp}')
        
    #     return '\n'.join(mermaid_lines)
    
    def generate_html_visualization(self) -> str:
        """Generate an interactive HTML visualization using D3.js"""
        all_modules = set()
        all_modules.update(self.module_imports.keys())
        all_modules.update(self.module_metrics.keys())
        all_modules.update(m.get('module', '') for m in self.function_locations.values())
        all_modules.update(self.class_info.keys())
        all_modules.discard('')  
        
        nodes = []
        links = []
        node_lookup = {}

        for module in all_modules:
            node_id = len(nodes)
            node_lookup[module] = node_id
            nodes.append({
                "id": node_id,
                "name": module,
                "type": "module"
            })

        for module, classes in self.class_info.items():
            if module not in node_lookup:  
                node_id = len(nodes)
                node_lookup[module] = node_id
                nodes.append({
                    "id": node_id,
                    "name": module,
                    "type": "module"
                })
                
            for class_name, info in classes.items():
                node_id = len(nodes)
                node_key = f"{module}.{class_name}"
                node_lookup[node_key] = node_id
                nodes.append({
                    "id": node_id,
                    "name": class_name,
                    "type": "class"
                })
                links.append({
                    "source": node_lookup[module],
                    "target": node_id,
                    "type": "contains"
                })

        for func_name, location in self.function_locations.items():
            if 'module' not in location:
                continue
                
            module = location['module']
            if module not in node_lookup:
                node_id = len(nodes)
                node_lookup[module] = node_id
                nodes.append({
                    "id": node_id,
                    "name": module,
                    "type": "module"
                })
            
            node_id = len(nodes)
            node_key = f"{module}.{func_name}"
            node_lookup[node_key] = node_id
            nodes.append({
                "id": node_id,
                "name": func_name,
                "type": "function"
            })
            links.append({
                "source": node_lookup[module],
                "target": node_id,
                "type": "contains"
            })

        for func_name, calls in self.function_calls.items():
            if func_name not in self.function_locations:
                continue
            if 'module' not in self.function_locations[func_name]:
                continue
                
            target_module = self.function_locations[func_name]['module']
            target_key = f"{target_module}.{func_name}"
            
            for call in calls:
                source_key = f"{call['from_module']}.{call['from_function']}"
                if source_key in node_lookup and target_key in node_lookup:
                    links.append({
                        "source": node_lookup[source_key],
                        "target": node_lookup[target_key],
                        "type": "calls"
                    })

        for module, imports in self.module_imports.items():
            if module in node_lookup:
                for imp in imports:
                    if imp in node_lookup:
                        links.append({
                            "source": node_lookup[module],
                            "target": node_lookup[imp],
                            "type": "imports"
                        })

        graph_data = {
            "nodes": nodes,
            "links": links
        }

        json_data = json.dumps(graph_data)

        return self.html_template.replace('GRAPH_DATA_PLACEHOLDER', json_data)
    
    def generate_summary_report(self) -> str:
        """Generate a readable markdown report with a link to the interactive visualization."""
        html_content = self.generate_html_visualization()
        viz_path = 'code_visualization.html'
        
        with open(viz_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        lines = ["# Code Analysis Summary Report\n"]
        
        lines.append(f"[Click here to open Interactive Code Visualization](./{viz_path})\n")
        
        lines.append("## Module Metrics\n")
        for module, metrics in sorted(self.module_metrics.items()):
            lines.append(f"### {module}")
            lines.append(f"- Functions: **{metrics['functions']}**")
            lines.append(f"- Classes: **{metrics['classes']}**")
            lines.append(f"- Complexity: **{metrics['complexity']}**")
            
            if module in self.class_info:
                lines.append("\nClasses:")
                for class_name, info in self.class_info[module].items():
                    lines.append(f"\n#### 📦 {class_name}")
                    lines.append(f"- Defined at line {info['line']}")
                    if info['methods']:
                        lines.append("- Methods:")
                        for method_name, method_info in info['methods'].items():
                            lines.append(f"  - ⚡ {method_name} (line {method_info['line']})")
                            if method_info['calls']:
                                lines.append(f"    Calls: {', '.join(method_info['calls'])}")
            
            functions_in_module = [f for f, loc in self.function_locations.items() 
                                if loc['module'] == module and 'in_class' not in loc]
            if functions_in_module:
                lines.append("\nFunctions:")
                for func in functions_in_module:
                    lines.append(f"\n#### ⚡ {func}")
                    if func in self.function_calls:
                        lines.append("Called by:")
                        for call in self.function_calls[func]:
                            lines.append(f"- {call['from_function']} in {call['from_module']} (line {call['line']})")
            
            lines.append("") 
        
        lines.append("## Complexity Hotspots\n")
        if self.complex_functions:
            sorted_hotspots = sorted(self.complex_functions, key=lambda x: x[2], reverse=True)
            for module, func, complexity in sorted_hotspots:
                lines.append(f"### {func}")
                lines.append(f"- **Module**: {module}")
                lines.append(f"- **Complexity**: {complexity}")
                lines.append("")
        else:
            lines.append("*No complex functions found.*\n")
        
        return '\n'.join(lines)