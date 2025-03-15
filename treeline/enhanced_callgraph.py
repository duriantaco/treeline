# import ast
# import inspect
# import re
# import networkx as nx
# from collections import defaultdict
# from pathlib import Path
# from typing import Dict, List, Set, Tuple, Optional, Any, Union
# import builtins
# import typing
# from dataclasses import dataclass

# @dataclass
# class TypeInfo:
#     inferred_type: str
#     confidence: float
#     source_locations: List[Tuple[str, int]]
#     possible_values: List[Any] = None

# @dataclass
# class ParameterInfo:
#     name: str
#     type_info: TypeInfo
#     default_value: Any = None
#     is_required: bool = True
#     usages: List[Tuple[str, int]] = None
#     mutations: List[Tuple[str, int]] = None

# @dataclass
# class ReturnInfo:
#     inferred_type: str
#     return_paths: List[Tuple[str, int]]
#     possible_values: List[Any] = None
#     conditions: List[str] = None

# @dataclass
# class FunctionBehavior:
#     pure: bool = False
#     idempotent: bool = False
#     recursive: bool = False
#     mutates_parameters: bool = False
#     mutates_globals: bool = False
#     has_side_effects: bool = True
#     reads_globals: bool = False
#     exception_paths: List[Tuple[str, str, int]] = None
#     io_operations: List[str] = None
#     deterministic: bool = False
#     complexity: int = 0
#     cognitive_complexity: int = 0

# @dataclass
# class CallContext:
#     call_site: Tuple[str, int]
#     passed_arguments: Dict[str, Any]
#     arg_data_sources: Dict[str, List[str]]
#     containing_branch_conditions: List[str]
#     call_frequency: int = 1
#     is_conditional: bool = False
#     controlling_vars: List[str] = None
#     call_chain_depth: int = 0

# @dataclass
# class DataFlowPath:
#     source: str
#     sink: str
#     intermediates: List[str]
#     transforms: List[str]
#     path_conditions: List[str] = None
#     sensitive: bool = False

# class EnrichedCallGraph:
#     def __init__(self):
#         self.graph = nx.DiGraph()
#         self.modules = {}
#         self.functions = {}
#         self.classes = {}
#         self.type_info = {}
#         self.behaviors = {}
#         self.data_flows = []
#         self.call_contexts = defaultdict(list)
#         self.state_mutations = defaultdict(list)
#         self.control_patterns = defaultdict(list)
#         self.error_flows = defaultdict(list)
#         self.global_vars = {}
#         self.module_dependencies = defaultdict(set)
#         self.variable_defs = defaultdict(dict)
#         self.imported_modules = defaultdict(dict)
#         self.aliases = {}
        
#         self.known_types = {
#             **{name: name for name in dir(builtins) if isinstance(getattr(builtins, name), type)},
#             **{name: f"typing.{name}" for name in dir(typing) if not name.startswith('_')}
#         }
        
#         self.builtin_callables = {
#             name: {"pure": name not in ["print", "input", "open", "write", "exit", "quit"]} 
#             for name in dir(builtins) if callable(getattr(builtins, name))
#         }
        
#         self.security_sinks = {
#             "sql": ["execute", "executemany", "cursor.execute", "raw_query"],
#             "command": ["os.system", "subprocess.run", "subprocess.Popen", "eval", "exec"],
#             "file": ["open", "read", "write", "load", "loads", "pickle.loads"],
#             "http": ["requests.get", "requests.post", "urllib.request.urlopen"]
#         }
    
#     def analyze_directory(self, directory: Path):
#         for file_path in directory.rglob("*.py"):
#             self.analyze_file(file_path)
            
#         self._build_cross_module_data_flows()
#         self._detect_patterns()
#         self._analyze_security_dataflows()
#         return self
    
#     def analyze_file(self, file_path: Path):
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 content = f.read()
                
#             module_name = str(file_path.stem)
#             rel_path = str(file_path)
#             self.modules[rel_path] = {"name": module_name, "path": rel_path}
            
#             tree = ast.parse(content)
#             self._analyze_imports(tree, module_name, rel_path)
            
#             global_analyzer = GlobalVariableAnalyzer(module_name, rel_path)
#             global_analyzer.visit(tree)
#             self.global_vars.update(global_analyzer.globals)
            
#             function_analyzer = FunctionAnalyzer(self, module_name, rel_path, content)
#             function_analyzer.visit(tree)
            
#             class_analyzer = ClassAnalyzer(self, module_name, rel_path, content)
#             class_analyzer.visit(tree)
            
#             call_analyzer = CallAnalyzer(self, module_name, rel_path, content)
#             call_analyzer.visit(tree)
            
#             data_flow_analyzer = DataFlowAnalyzer(self, module_name, rel_path, content)
#             data_flow_analyzer.visit(tree)
            
#         except Exception as e:
#             print(f"Error analyzing {file_path}: {e}")
    
#     def _analyze_imports(self, tree: ast.AST, module_name: str, file_path: str):
#         for node in ast.walk(tree):
#             if isinstance(node, ast.Import):
#                 for name in node.names:
#                     alias = name.asname or name.name
#                     self.imported_modules[module_name][alias] = name.name
#                     self.aliases[f"{module_name}.{alias}"] = name.name
#                     self.module_dependencies[module_name].add(name.name)
                    
#             elif isinstance(node, ast.ImportFrom):
#                 if node.module:
#                     base_module = node.module
#                     for name in node.names:
#                         imported_name = name.name
#                         alias = name.asname or imported_name
#                         full_name = f"{base_module}.{imported_name}"
#                         self.imported_modules[module_name][alias] = full_name
#                         self.aliases[f"{module_name}.{alias}"] = full_name
#                         self.module_dependencies[module_name].add(base_module)
    
#     def _build_cross_module_data_flows(self):
#         from collections import defaultdict
#         source_to_flows = defaultdict(list)
#         for flow in self.data_flows:
#             source_to_flows[flow.source].append(flow)
        
#         new_flows = []
#         for source_flow in self.data_flows:
#             if source_flow.sink in source_to_flows:
#                 for sink_flow in source_to_flows[source_flow.sink]:
#                     combined_flow = DataFlowPath(
#                         source=source_flow.source,
#                         sink=sink_flow.sink,
#                         intermediates=source_flow.intermediates + [source_flow.sink] + sink_flow.intermediates,
#                         transforms=source_flow.transforms + sink_flow.transforms,
#                         path_conditions=(source_flow.path_conditions or []) + (sink_flow.path_conditions or []),
#                         sensitive=source_flow.sensitive or sink_flow.sensitive
#                     )
#                     new_flows.append(combined_flow)
#         self.data_flows.extend(new_flows)
    
#     def _detect_patterns(self):
#         for func_name, behaviors in self.behaviors.items():
#             node_attrs = self.graph.nodes.get(func_name, {})
#             if behaviors.recursive:
#                 node_attrs['pattern'] = 'recursive'
#             if not behaviors.mutates_parameters and not behaviors.mutates_globals and not behaviors.has_side_effects:
#                 node_attrs['pattern'] = 'pure'
            
#             in_degree = self.graph.in_degree(func_name) or 0
#             out_degree = self.graph.out_degree(func_name) or 0
            
#             if in_degree > 5 and out_degree <= 1:
#                 node_attrs['pattern'] = 'collector'
#             if in_degree <= 1 and out_degree > 5:
#                 node_attrs['pattern'] = 'dispatcher'
#             if behaviors.complexity > 15:
#                 node_attrs['pattern'] = 'complex_decision'
            
#             if node_attrs:
#                 self.graph.nodes[func_name].update(node_attrs)
    
#     def _analyze_security_dataflows(self):
#         for flow in self.data_flows:
#             for category, sinks in self.security_sinks.items():
#                 if any(sink in flow.sink for sink in sinks):
#                     flow.sensitive = True
#                     for func_name in [flow.source] + flow.intermediates + [flow.sink]:
#                         if func_name in self.graph.nodes:
#                             node_attrs = self.graph.nodes[func_name]
#                             security_issues = node_attrs.get('security_issues', [])
#                             security_issues.append({
#                                 'type': f'potential_{category}_injection',
#                                 'flow': f"{flow.source} -> {flow.sink}",
#                                 'severity': 'high' if not flow.transforms else 'medium'
#                             })
#                             node_attrs['security_issues'] = security_issues
#                             self.graph.nodes[func_name].update(node_attrs)
#                     break  
            
#     def get_dependencies_for_function(self, func_name: str, depth: int = 1):
#         if func_name not in self.graph:
#             return []
        
#         if depth == 1:
#             return list(self.graph.successors(func_name))
        
#         result = set()
#         visited = set()
#         queue = [(func_name, 0)]
        
#         while queue:
#             current, current_depth = queue.pop(0)
#             if current in visited:
#                 continue
                
#             visited.add(current)
#             if current != func_name:
#                 result.add(current)
                
#             if current_depth < depth:
#                 for neighbor in self.graph.successors(current):
#                     queue.append((neighbor, current_depth + 1))
                    
#         return list(result)
    
#     def get_dependents_for_function(self, func_name: str, depth: int = 1):
#         if func_name not in self.graph:
#             return []
        
#         if depth == 1:
#             return list(self.graph.predecessors(func_name))
        
#         result = set()
#         visited = set()
#         queue = [(func_name, 0)]
        
#         while queue:
#             current, current_depth = queue.pop(0)
#             if current in visited:
#                 continue
                
#             visited.add(current)
#             if current != func_name:
#                 result.add(current)
                
#             if current_depth < depth:
#                 for neighbor in self.graph.predecessors(current):
#                     queue.append((neighbor, current_depth + 1))
                    
#         return list(result)
    
#     def get_impacted_by_change(self, func_name: str):
#         impacted = set(self.get_dependents_for_function(func_name, depth=100))
        
#         for flow in self.data_flows:
#             if func_name == flow.source or func_name in flow.intermediates:
#                 impacted.add(flow.sink)
                
#         return list(impacted)
    
#     def get_required_changes(self, func_name: str, change_type: str):
#         if change_type == "signature":
#             impacted = []
#             for caller in self.get_dependents_for_function(func_name):
#                 contexts = self.call_contexts.get((caller, func_name), [])
#                 for context in contexts:
#                     impacted.append((caller, context.call_site))
#             return impacted
            
#         elif change_type == "behavior":
#             return self.get_impacted_by_change(func_name)
            
#         elif change_type == "removal":
#             return self.get_dependents_for_function(func_name, depth=1)
            
#         return []
    
#     def get_function_summary(self, func_name: str):
#         if func_name not in self.functions:
#             return {}
            
#         func_info = self.functions[func_name]
#         behavior = self.behaviors.get(func_name, FunctionBehavior())
        
#         return {
#             "name": func_name,
#             "module": func_info.get("module", ""),
#             "file_path": func_info.get("file_path", ""),
#             "line": func_info.get("line", 0),
#             "parameters": func_info.get("parameters", {}),
#             "return_info": func_info.get("return_info", {}),
#             "docstring": func_info.get("docstring", ""),
#             "behavior": {
#                 "pure": behavior.pure,
#                 "idempotent": behavior.idempotent,
#                 "recursive": behavior.recursive,
#                 "has_side_effects": behavior.has_side_effects,
#                 "complexity": behavior.complexity,
#                 "cognitive_complexity": behavior.cognitive_complexity
#             },
#             "calls": [
#                 {
#                     "target": target,
#                     "contexts": [
#                         {
#                             "line": ctx.call_site[1],
#                             "arguments": ctx.passed_arguments,
#                             "conditional": ctx.is_conditional
#                         }
#                         for ctx in self.call_contexts.get((func_name, target), [])
#                     ]
#                 }
#                 for target in self.get_dependencies_for_function(func_name)
#             ],
#             "called_by": [
#                 {
#                     "caller": caller,
#                     "contexts": [
#                         {
#                             "line": ctx.call_site[1],
#                             "arguments": ctx.passed_arguments,
#                             "conditional": ctx.is_conditional
#                         }
#                         for ctx in self.call_contexts.get((caller, func_name), [])
#                     ]
#                 }
#                 for caller in self.get_dependents_for_function(func_name)
#             ],
#             "data_flows": [
#                 {
#                     "source": flow.source,
#                     "sink": flow.sink,
#                     "transformations": flow.transforms,
#                     "sensitive": flow.sensitive
#                 }
#                 for flow in self.data_flows
#                 if flow.source == func_name or flow.sink == func_name or func_name in flow.intermediates
#             ]
#         }
    
#     def get_json_for_llm(self):
#         return {
#             "modules": self.modules,
#             "functions": {
#                 name: self.get_function_summary(name)
#                 for name in self.functions
#             },
#             "classes": self.classes,
#             "data_flows": [
#                 {
#                     "source": flow.source,
#                     "sink": flow.sink,
#                     "intermediates": flow.intermediates,
#                     "transforms": flow.transforms,
#                     "sensitive": flow.sensitive
#                 }
#                 for flow in self.data_flows
#             ],
#             "module_dependencies": {
#                 module: list(deps)
#                 for module, deps in self.module_dependencies.items()
#             },
#             "patterns": {
#                 node: data.get('pattern')
#                 for node, data in self.graph.nodes(data=True)
#                 if 'pattern' in data
#             },
#             "security_issues": {
#                 node: data.get('security_issues')
#                 for node, data in self.graph.nodes(data=True)
#                 if 'security_issues' in data
#             }
#         }

# class FunctionAnalyzer(ast.NodeVisitor):
#     def __init__(self, graph: EnrichedCallGraph, module_name: str, file_path: str, content: str):
#         self.graph = graph
#         self.module_name = module_name
#         self.file_path = file_path
#         self.content = content.split('\n')
#         self.class_stack = []
#         self.current_function = None
        
#     def visit_FunctionDef(self, node):
#         if self.class_stack:
#             class_name = self.class_stack[-1]
#             func_name = f"{self.module_name}.{class_name}.{node.name}"
#             is_method = True
#         else:
#             func_name = f"{self.module_name}.{node.name}"
#             is_method = False
        
#         docstring = ast.get_docstring(node)
        
#         param_info = {}
#         for i, arg in enumerate(node.args.args):
#             if i == 0 and is_method and arg.arg == 'self':
#                 continue
                
#             arg_name = arg.arg
#             type_annotation = None
            
#             if arg.annotation:
#                 if isinstance(arg.annotation, ast.Name):
#                     type_annotation = arg.annotation.id
#                 elif isinstance(arg.annotation, ast.Attribute):
#                     type_annotation = f"{arg.annotation.value.id}.{arg.annotation.attr}"
#                 elif isinstance(arg.annotation, ast.Subscript):
#                     if isinstance(arg.annotation.value, ast.Name):
#                         container = arg.annotation.value.id
#                         if isinstance(arg.annotation.slice, ast.Name):
#                             param = arg.annotation.slice.id
#                             type_annotation = f"{container}[{param}]"
            
#             default_idx = len(node.args.args) - len(node.args.defaults)
#             default_value = None
#             is_required = True
            
#             if i >= default_idx:
#                 default_value_node = node.args.defaults[i - default_idx]
#                 if isinstance(default_value_node, ast.Constant):
#                     default_value = default_value_node.value
#                 is_required = False
            
#             param_info[arg_name] = ParameterInfo(
#                 name=arg_name,
#                 type_info=TypeInfo(
#                     inferred_type=type_annotation or "unknown",
#                     confidence=1.0 if type_annotation else 0.5,
#                     source_locations=[(self.file_path, node.lineno)]
#                 ),
#                 default_value=default_value,
#                 is_required=is_required,
#                 usages=[],
#                 mutations=[]
#             )
        
#         return_info = None
#         if node.returns:
#             if isinstance(node.returns, ast.Name):
#                 return_type = node.returns.id
#             elif isinstance(node.returns, ast.Attribute):
#                 return_type = f"{node.returns.value.id}.{node.returns.attr}"
#             else:
#                 return_type = "complex"
                
#             return_info = ReturnInfo(
#                 inferred_type=return_type,
#                 return_paths=[],
#                 possible_values=None,
#                 conditions=None
#             )
        
#         self.graph.functions[func_name] = {
#             "name": node.name,
#             "module": self.module_name,
#             "class": self.class_stack[-1] if self.class_stack else None,
#             "file_path": self.file_path,
#             "line": node.lineno,
#             "end_line": node.end_lineno,
#             "parameters": param_info,
#             "return_info": return_info,
#             "docstring": docstring
#         }
        
#         self.graph.graph.add_node(func_name, 
#                                   type='function', 
#                                   module=self.module_name,
#                                   file_path=self.file_path,
#                                   line=node.lineno)
        
#         self.current_function = func_name
#         complexity = self._calculate_complexity(node)
#         cognitive_complexity = self._calculate_cognitive_complexity(node)
        
#         behavior = FunctionBehavior(
#             recursive=self._is_recursive(node, func_name),
#             mutates_parameters=self._mutates_parameters(node),
#             mutates_globals=self._accesses_globals(node, write=True),
#             reads_globals=self._accesses_globals(node, write=False),
#             pure=not (self._mutates_parameters(node) or 
#                       self._accesses_globals(node, write=True) or
#                       self._has_side_effects(node)),
#             has_side_effects=self._has_side_effects(node),
#             exception_paths=self._find_exception_paths(node),
#             io_operations=self._find_io_operations(node),
#             complexity=complexity,
#             cognitive_complexity=cognitive_complexity,
#             deterministic=not self._has_nondeterministic_calls(node)
#         )
        
#         self.graph.behaviors[func_name] = behavior
        
#         self.generic_visit(node)
#         self.current_function = None
        
#     def visit_ClassDef(self, node):
#         class_name = f"{self.module_name}.{node.name}"
#         docstring = ast.get_docstring(node)
        
#         base_classes = []
#         for base in node.bases:
#             if isinstance(base, ast.Name):
#                 base_classes.append(base.id)
#             elif isinstance(base, ast.Attribute):
#                 base_classes.append(f"{base.value.id}.{base.attr}")
        
#         self.graph.classes[class_name] = {
#             "name": node.name,
#             "module": self.module_name,
#             "file_path": self.file_path,
#             "line": node.lineno,
#             "end_line": node.end_lineno,
#             "docstring": docstring,
#             "bases": base_classes,
#             "methods": []
#         }
        
#         self.class_stack.append(node.name)
#         self.generic_visit(node)
#         self.class_stack.pop()
        
#     def _calculate_complexity(self, node):
#         complexity = 1
#         for child in ast.walk(node):
#             if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
#                 complexity += 1
#             elif isinstance(child, ast.BoolOp) and isinstance(child.op, (ast.And, ast.Or)):
#                 complexity += len(child.values) - 1
#         return complexity
    
#     def _calculate_cognitive_complexity(self, node):
#         def process_node(node, nesting=0):
#             complexity = 0
#             if isinstance(node, (ast.If, ast.For, ast.While)):
#                 complexity += nesting + 1
#                 for child in ast.iter_child_nodes(node):
#                     complexity += process_node(child, nesting + 1)
#             elif isinstance(node, ast.BoolOp):
#                 complexity += len(node.values) - 1
#             else:
#                 for child in ast.iter_child_nodes(node):
#                     complexity += process_node(child, nesting)
#             return complexity
        
#         return process_node(node)
    
#     def _is_recursive(self, node, func_name):
#         class RecursiveCallFinder(ast.NodeVisitor):
#             def __init__(self, func_name):
#                 self.func_name = func_name.split('.')[-1]
#                 self.has_recursive_call = False
                
#             def visit_Call(self, node):
#                 if isinstance(node.func, ast.Name) and node.func.id == self.func_name:
#                     self.has_recursive_call = True
#                 self.generic_visit(node)
        
#         finder = RecursiveCallFinder(func_name)
#         finder.visit(node)
#         return finder.has_recursive_call
    
#     def _mutates_parameters(self, node):
#         class ParameterMutationFinder(ast.NodeVisitor):
#             def __init__(self, param_names):
#                 self.param_names = param_names
#                 self.mutates = False
                
#             def visit_Assign(self, node):
#                 for target in node.targets:
#                     if isinstance(target, ast.Name) and target.id in self.param_names:
#                         self.mutates = True
#                     elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id in self.param_names:
#                         self.mutates = True
#                 self.generic_visit(node)
                
#             def visit_AugAssign(self, node):
#                 if isinstance(node.target, ast.Name) and node.target.id in self.param_names:
#                     self.mutates = True
#                 elif isinstance(node.target, ast.Attribute) and isinstance(node.target.value, ast.Name) and node.target.value.id in self.param_names:
#                     self.mutates = True
#                 self.generic_visit(node)
        
#         param_names = [arg.arg for arg in node.args.args]
#         finder = ParameterMutationFinder(param_names)
#         finder.visit(node)
#         return finder.mutates
    
#     def _accesses_globals(self, node, write=False):
#         class GlobalAccessFinder(ast.NodeVisitor):
#             def __init__(self, global_vars, write=False):
#                 self.global_vars = global_vars
#                 self.write = write
#                 self.accesses = False
                
#             def visit_Global(self, node):
#                 if not self.write:
#                     self.accesses = True
#                 self.generic_visit(node)
                
#             def visit_Name(self, node):
#                 if node.id in self.global_vars:
#                     self.accesses = True
#                 self.generic_visit(node)
                
#             def visit_Assign(self, node):
#                 if not self.write:
#                     self.generic_visit(node)
#                     return
                
#                 for target in node.targets:
#                     if isinstance(target, ast.Name) and target.id in self.global_vars:
#                         self.accesses = True
#                 self.generic_visit(node)
        
#         module_globals = [name for name, info in self.graph.global_vars.items() 
#                           if info.get('module') == self.module_name]
#         finder = GlobalAccessFinder(module_globals, write)
#         finder.visit(node)
#         return finder.accesses
    
#     def _has_side_effects(self, node):
#         class SideEffectFinder(ast.NodeVisitor):
#             def __init__(self):
#                 self.has_side_effects = False
#                 self.side_effect_funcs = {
#                     'print', 'open', 'write', 'close', 'append',
#                     'extend', 'insert', 'remove', 'pop', 'clear',
#                     'update', 'create', 'delete', 'save', 'load'
#                 }
                
#             def visit_Call(self, node):
#                 if isinstance(node.func, ast.Name) and node.func.id in self.side_effect_funcs:
#                     self.has_side_effects = True
#                 elif isinstance(node.func, ast.Attribute) and node.func.attr in self.side_effect_funcs:
#                     self.has_side_effects = True
#                 self.generic_visit(node)
        
#         finder = SideEffectFinder()
#         finder.visit(node)
#         return finder.has_side_effects
    
#     def _find_exception_paths(self, node):
#         exception_paths = []
#         for child in ast.walk(node):
#             if isinstance(child, ast.Raise):
#                 if isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
#                     exception_paths.append((child.exc.func.id, "", child.lineno))
#                 elif isinstance(child.exc, ast.Name):
#                     exception_paths.append((child.exc.id, "", child.lineno))
#             elif isinstance(child, ast.Try):
#                 exception_paths.append(("try-except", "", child.lineno))
#         return exception_paths
    
#     def _find_io_operations(self, node):
#         io_ops = []
#         for child in ast.walk(node):
#             if isinstance(child, ast.Call):
#                 if isinstance(child.func, ast.Name) and child.func.id in ['open', 'print', 'input']:
#                     io_ops.append(child.func.id)
#                 elif isinstance(child.func, ast.Attribute) and child.func.attr in ['read', 'write', 'readline', 'readlines']:
#                     io_ops.append(child.func.attr)
#         return io_ops
    
#     def _has_nondeterministic_calls(self, node):
#         nondeterministic_funcs = {'random', 'randint', 'choice', 'shuffle', 'sample', 'uuid', 'now', 'today', 'datetime'}
        
#         for child in ast.walk(node):
#             if isinstance(child, ast.Call):
#                 if isinstance(child.func, ast.Name) and child.func.id in nondeterministic_funcs:
#                     return True
#                 elif isinstance(child.func, ast.Attribute) and child.func.attr in nondeterministic_funcs:
#                     return True
#         return False

# class CallAnalyzer(ast.NodeVisitor):
#     def __init__(self, graph: EnrichedCallGraph, module_name: str, file_path: str, content: str):
#         self.graph = graph
#         self.module_name = module_name
#         self.file_path = file_path
#         self.content = content.split('\n')
#         self.class_stack = []
#         self.current_function = None
#         self.conditional_depth = 0
#         self.conditions = []
        
#     def visit_FunctionDef(self, node):
#         if self.class_stack:
#             class_name = self.class_stack[-1]
#             func_name = f"{self.module_name}.{class_name}.{node.name}"
#         else:
#             func_name = f"{self.module_name}.{node.name}"
        
#         self.current_function = func_name
#         self.generic_visit(node)
#         self.current_function = None
    
#     def visit_ClassDef(self, node):
#         self.class_stack.append(node.name)
#         self.generic_visit(node)
#         self.class_stack.pop()
    
#     def visit_If(self, node):
#         self.conditional_depth += 1
#         condition_text = self.content[node.lineno - 1].strip()
#         self.conditions.append(condition_text)
#         self.generic_visit(node)
#         self.conditions.pop()
#         self.conditional_depth -= 1
        
#     def visit_For(self, node):
#         self.conditional_depth += 1
#         condition_text = self.content[node.lineno - 1].strip()
#         self.conditions.append(condition_text)
#         self.generic_visit(node)
#         self.conditions.pop()
#         self.conditional_depth -= 1
        
#     def visit_While(self, node):
#         self.conditional_depth += 1
#         condition_text = self.content[node.lineno - 1].strip()
#         self.conditions.append(condition_text)
#         self.generic_visit(node)
#         self.conditions.pop()
#         self.conditional_depth -= 1
    
#     def visit_Call(self, node):
#         if not self.current_function:
#             self.generic_visit(node)
#             return
            
#         target_func = self._resolve_call_target(node)
#         if not target_func:
#             self.generic_visit(node)
#             return
            
#         source_func = self.current_function
        
#         self.graph.graph.add_edge(source_func, target_func, type='call')
        
#         call_line = self.content[node.lineno - 1] if node.lineno <= len(self.content) else ""
#         arg_values = {}
#         arg_sources = {}
        
#         for i, arg in enumerate(node.args):
#             if isinstance(arg, ast.Constant):
#                 arg_values[f"arg{i}"] = arg.value
#             elif isinstance(arg, ast.Name):
#                 arg_values[f"arg{i}"] = arg.id
#                 arg_sources[f"arg{i}"] = [arg.id]
                
#         for kw in node.keywords:
#             if isinstance(kw.value, ast.Constant):
#                 arg_values[kw.arg] = kw.value.value
#             elif isinstance(kw.value, ast.Name):
#                 arg_values[kw.arg] = kw.value.id
#                 arg_sources[kw.arg] = [kw.value.id]
                
#         context = CallContext(
#             call_site=(self.file_path, node.lineno),
#             passed_arguments=arg_values,
#             arg_data_sources=arg_sources,
#             containing_branch_conditions=self.conditions.copy(),
#             is_conditional=self.conditional_depth > 0,
#             controlling_vars=self._extract_condition_vars(),
#             call_chain_depth=0
#         )
        
#         self.graph.call_contexts[(source_func, target_func)].append(context)
        
#         self.generic_visit(node)
    
#     def _resolve_call_target(self, node):
#         if isinstance(node.func, ast.Name):
#             func_name = node.func.id
#             if func_name in self.graph.functions:
#                 return func_name
                
#             in_module = f"{self.module_name}.{func_name}"
#             if in_module in self.graph.functions:
#                 return in_module
                
#             imported = self.graph.imported_modules.get(self.module_name, {}).get(func_name)
#             if imported:
#                 return imported
                
#         elif isinstance(node.func, ast.Attribute):
#             if isinstance(node.func.value, ast.Name):
#                 module_or_var = node.func.value.id
#                 attr_name = node.func.attr
                
#                 imported = self.graph.imported_modules.get(self.module_name, {}).get(module_or_var)
#                 if imported:
#                     return f"{imported}.{attr_name}"
                
#                 full_name = f"{module_or_var}.{attr_name}"
#                 if full_name in self.graph.functions:
#                     return full_name
                
#                 if self.class_stack and module_or_var == 'self':
#                     class_name = self.class_stack[-1]
#                     return f"{self.module_name}.{class_name}.{attr_name}"
                    
#         return None
    
#     def _extract_condition_vars(self):
#         vars = []
#         for condition in self.conditions:
#             vars.extend(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', condition))
#         return list(set(vars))

# class GlobalVariableAnalyzer(ast.NodeVisitor):
#     def __init__(self, module_name: str, file_path: str):
#         self.module_name = module_name
#         self.file_path = file_path
#         self.globals = {}
        
#     def visit_Assign(self, node):
#         if isinstance(node.targets[0], ast.Name):
#             var_name = node.targets[0].id
#             if var_name.isupper() or not hasattr(node, 'parent') or not isinstance(node.parent, ast.FunctionDef):
#                 self.globals[var_name] = {
#                     'module': self.module_name,
#                     'file': self.file_path,
#                     'line': node.lineno
#                 }
#         self.generic_visit(node)
    
#     def visit_AnnAssign(self, node):
#         if isinstance(node.target, ast.Name):
#             var_name = node.target.id
#             if var_name.isupper() or not hasattr(node, 'parent') or not isinstance(node.parent, ast.FunctionDef):
#                 type_annotation = None
#                 if node.annotation:
#                     if isinstance(node.annotation, ast.Name):
#                         type_annotation = node.annotation.id
                
#                 self.globals[var_name] = {
#                     'module': self.module_name,
#                     'file': self.file_path,
#                     'line': node.lineno,
#                     'type': type_annotation
#                 }
#         self.generic_visit(node)

# class ClassAnalyzer(ast.NodeVisitor):
#     def __init__(self, graph: EnrichedCallGraph, module_name: str, file_path: str, content: str):
#         self.graph = graph
#         self.module_name = module_name
#         self.file_path = file_path
#         self.content = content.split('\n')
        
#     def visit_ClassDef(self, node):
#         class_name = f"{self.module_name}.{node.name}"
        
#         if class_name in self.graph.classes:
#             methods = []
            
#             for child in node.body:
#                 if isinstance(child, ast.FunctionDef):
#                     method_name = f"{class_name}.{child.name}"
#                     methods.append(method_name)
                    
#             self.graph.classes[class_name]["methods"] = methods
            
#             for method in methods:
#                 if method in self.graph.functions:
#                     self.graph.functions[method]["class"] = class_name
        
#         self.generic_visit(node)

# class DataFlowAnalyzer(ast.NodeVisitor):
#     def __init__(self, graph: EnrichedCallGraph, module_name: str, file_path: str, content: str):
#         self.graph = graph
#         self.module_name = module_name
#         self.file_path = file_path
#         self.content = content.split('\n')
#         self.class_stack = []
#         self.current_function = None
#         self.var_defs = {}
#         self.var_uses = defaultdict(list)
#         self.conditions = []
#         self.sensitivity_labels = {
#             'password': True, 'secret': True, 'token': True, 'key': True,
#             'credential': True, 'auth': True, 'jwt': True, 'api_key': True
#         }
        
#     def visit_FunctionDef(self, node):
#         if self.class_stack:
#             class_name = self.class_stack[-1]
#             func_name = f"{self.module_name}.{class_name}.{node.name}"
#         else:
#             func_name = f"{self.module_name}.{node.name}"
        
#         self.current_function = func_name
#         old_vars = self.var_defs.copy()
#         self.var_defs = {}
        
#         for arg in node.args.args:
#             self.var_defs[arg.arg] = {
#                 'source': 'parameter',
#                 'function': func_name,
#                 'line': node.lineno,
#                 'sensitive': self._is_sensitive(arg.arg)
#             }
        
#         self.generic_visit(node)
        
#         for var_name, uses in self.var_uses.items():
#             if var_name in self.var_defs:
#                 source = self.var_defs[var_name]
#                 for use in uses:
#                     if use['function'] == func_name and source['function'] == func_name:
#                         continue
                    
#                     source_func = source['function']
#                     sink_func = use['function']
                    
#                     flow = DataFlowPath(
#                         source=source_func,
#                         sink=sink_func,
#                         intermediates=[],
#                         transforms=[],
#                         path_conditions=self.conditions.copy(),
#                         sensitive=source.get('sensitive', False) or use.get('sensitive', False)
#                     )
                    
#                     self.graph.data_flows.append(flow)
        
#         self.var_defs = old_vars
#         self.current_function = None
    
#     def visit_ClassDef(self, node):
#         self.class_stack.append(node.name)
#         self.generic_visit(node)
#         self.class_stack.pop()
        
#     def visit_Assign(self, node):
#         if not self.current_function:
#             self.generic_visit(node)
#             return
            
#         for target in node.targets:
#             if isinstance(target, ast.Name):
#                 var_name = target.id
#                 source_info = {
#                     'source': 'assignment',
#                     'function': self.current_function,
#                     'line': node.lineno,
#                     'sensitive': self._is_sensitive(var_name)
#                 }
                
#                 if isinstance(node.value, ast.Call):
#                     called_func = self._resolve_call_target(node.value)
#                     if called_func:
#                         source_info['source'] = 'call'
#                         source_info['called_func'] = called_func
                        
#                         flow = DataFlowPath(
#                             source=called_func,
#                             sink=self.current_function,
#                             intermediates=[],
#                             transforms=[],
#                             path_conditions=self.conditions.copy(),
#                             sensitive=self._is_sensitive(var_name)
#                         )
                        
#                         self.graph.data_flows.append(flow)
                
#                 self.var_defs[var_name] = source_info
        
#         self.generic_visit(node)
    
#     def visit_Name(self, node):
#         if not self.current_function:
#             self.generic_visit(node)
#             return
            
#         if isinstance(node.ctx, ast.Load) and node.id in self.var_defs:
#             self.var_uses[node.id].append({
#                 'function': self.current_function,
#                 'line': node.lineno,
#                 'sensitive': self._is_sensitive(node.id) or self.var_defs[node.id].get('sensitive', False)
#             })
        
#         self.generic_visit(node)
        
#     def visit_If(self, node):
#         if not self.current_function:
#             self.generic_visit(node)
#             return
            
#         condition_text = self.content[node.lineno - 1].strip()
#         self.conditions.append(condition_text)
#         self.generic_visit(node)
#         self.conditions.pop()
        
#     def visit_Call(self, node):
#         if not self.current_function:
#             self.generic_visit(node)
#             return
            
#         target_func = self._resolve_call_target(node)
#         if not target_func:
#             self.generic_visit(node)
#             return
            
#         for i, arg in enumerate(node.args):
#             if isinstance(arg, ast.Name) and arg.id in self.var_defs:
#                 self.var_uses[arg.id].append({
#                     'function': target_func,
#                     'line': node.lineno,
#                     'sensitive': self._is_sensitive(arg.id) or self.var_defs[arg.id].get('sensitive', False),
#                     'as_argument': True,
#                     'arg_position': i
#                 })
        
#         self.generic_visit(node)
    
#     def _resolve_call_target(self, node):
#         if isinstance(node.func, ast.Name):
#             func_name = node.func.id
#             if func_name in self.graph.functions:
#                 return func_name
                
#             in_module = f"{self.module_name}.{func_name}"
#             if in_module in self.graph.functions:
#                 return in_module
                
#             imported = self.graph.imported_modules.get(self.module_name, {}).get(func_name)
#             if imported:
#                 return imported
                
#         elif isinstance(node.func, ast.Attribute):
#             if isinstance(node.func.value, ast.Name):
#                 module_or_var = node.func.value.id
#                 attr_name = node.func.attr
                
#                 imported = self.graph.imported_modules.get(self.module_name, {}).get(module_or_var)
#                 if imported:
#                     return f"{imported}.{attr_name}"
                
#                 full_name = f"{module_or_var}.{attr_name}"
#                 if full_name in self.graph.functions:
#                     return full_name
                
#                 if self.class_stack and module_or_var == 'self':
#                     class_name = self.class_stack[-1]
#                     return f"{self.module_name}.{class_name}.{attr_name}"
                    
#         return None
    
#     def _is_sensitive(self, var_name):
#         lower_name = var_name.lower()
#         return any(sensitive in lower_name for sensitive in self.sensitivity_labels)
    
#     def get_callgraph_report(self) -> Dict:
#         """Generate a report focused on call graph and data flow insights"""
#         categorized_functions = {
#             "pure_functions": [],
#             "side_effect_functions": [],
#             "recursive_functions": []
#         }
        
#         for func_name, behavior in self.call_graph.behaviors.items():
#             if behavior.pure:
#                 categorized_functions["pure_functions"].append(func_name)
#             if behavior.has_side_effects:
#                 categorized_functions["side_effect_functions"].append(func_name)
#             if behavior.recursive:
#                 categorized_functions["recursive_functions"].append(func_name)
        
#         data_flows = [
#             {
#                 "source": flow.source,
#                 "sink": flow.sink,
#                 "intermediates": flow.intermediates,
#                 "sensitive": flow.sensitive
#             }
#             for flow in self.call_graph.data_flows
#         ]
        
#         security_insights = self.call_graph.get_json_for_llm().get("security_issues", {})
        
#         return {
#             "function_categories": categorized_functions,
#             "data_flows": data_flows,
#             "security_insights": security_insights,
#             "patterns": self.call_graph.get_json_for_llm().get("patterns", {}),
#         }