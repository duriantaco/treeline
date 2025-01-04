# treeline/visualizers/mermaid.py
from typing import Dict, Set


class MermaidVisualizer:
    """Generates Mermaid diagrams for code visualization"""

    def generate_module_overview_diagram(
        self, module_imports: Dict[str, Set[str]]
    ) -> str:
        """
        Generate a Mermaid diagram showing modules and their relationships.

        Args:
            module_imports: Dictionary mapping modules to their imports
        """
        mermaid_lines = ["graph TD\n"]
        mermaid_lines.append("    %% Styling")
        mermaid_lines.append(
            "    classDef modNode fill:#b7e2d8,stroke:#333,stroke-width:2px\n"
        )

        added_nodes = set()
        for module in module_imports:
            clean_module = module.replace(".", "_")
            if clean_module not in added_nodes:
                mermaid_lines.append(f'    {clean_module}["{module}"]:::modNode')
                added_nodes.add(clean_module)

        mermaid_lines.append("")

        for module, imports in module_imports.items():
            clean_module = module.replace(".", "_")
            for imp in imports:
                if imp in module_imports:
                    clean_imp = imp.replace(".", "_")
                    mermaid_lines.append(f"    {clean_module} --> {clean_imp}")

        return "\n".join(mermaid_lines)

    def generate_module_detail_diagram(
        self,
        module: str,
        class_info: Dict[str, Dict],
        function_locations: Dict[str, Dict],
        function_calls: Dict[str, list],
    ) -> str:
        """
        Generate a Mermaid diagram showing functions and classes in a module.

        Args:
            module: Name of the module
            class_info: Dictionary of class information
            function_locations: Dictionary of function locations
            function_calls: Dictionary of function calls
        """
        mermaid_lines = ["graph TD\n"]
        mermaid_lines.append("    %% Styling")
        mermaid_lines.append("    classDef fnNode fill:#e4d1d1,stroke:#333")
        mermaid_lines.append("    classDef clsNode fill:#d1e0e4,stroke:#333\n")

        clean_module = module.replace(".", "_")
        added_nodes = set()

        mermaid_lines.append(f'    subgraph {clean_module}["{module}"]')
        mermaid_lines.append("        direction TB")

        module_classes = class_info.get(module, {})
        for class_name, info in module_classes.items():
            clean_class = f"{clean_module}_{class_name}"
            if clean_class not in added_nodes:
                mermaid_lines.append(
                    f'        {clean_class}["📦 {class_name}"]:::clsNode'
                )
                added_nodes.add(clean_class)

                for method_name in info["methods"]:
                    clean_method = f"{clean_class}_{method_name}"
                    if clean_method not in added_nodes:
                        mermaid_lines.append(
                            f'        {clean_method}["⚡ {method_name}"]:::fnNode'
                        )
                        mermaid_lines.append(
                            f"        {clean_class} --> {clean_method}"
                        )
                        added_nodes.add(clean_method)

        for func_name, location in function_locations.items():
            if location["module"] == module and "in_class" not in location:
                clean_func = f"{clean_module}_{func_name}"
                if clean_func not in added_nodes:
                    mermaid_lines.append(
                        f'        {clean_func}["⚡ {func_name}"]:::fnNode'
                    )
                    added_nodes.add(clean_func)

        mermaid_lines.append("    end\n")

        for func_name, calls in function_calls.items():
            if (
                func_name in function_locations
                and function_locations[func_name]["module"] == module
            ):
                to_func = f"{clean_module}_{func_name}"
                for call in calls:
                    if call["from_module"] == module:
                        from_func = f"{clean_module}_{call['from_function']}"
                        if from_func in added_nodes and to_func in added_nodes:
                            mermaid_lines.append(
                                f"    {from_func} -.->|calls| {to_func}"
                            )

        return "\n".join(mermaid_lines)
