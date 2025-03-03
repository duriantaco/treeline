from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

class ReportGenerator:
    def __init__(self, target_dir: Path, output_dir: Path = None):
        self.target_dir = target_dir
        self.output_dir = output_dir or Path("treeline_reports")
        self.output_dir.mkdir(exist_ok=True)

        from treeline.dependency_analyzer import ModuleDependencyAnalyzer
        from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

        self.dependency_analyzer = ModuleDependencyAnalyzer()
        self.enhanced_analyzer = EnhancedCodeAnalyzer()

        self.analyzed_files = []
        self.quality_issues = defaultdict(list)
        self.complexity_metrics = {}
        self.dependency_graph = {}
        self.entry_points = []
        self.core_components = []
        self.code_smells_by_category = defaultdict(list)
        self.issues_by_file = defaultdict(list)
        self.issues_count = 0

    def analyze(self):
        print(f"Analyzing {self.target_dir}...")

        for py_file in self.target_dir.rglob("*.py"):
            if not self._should_analyze_file(py_file):
                continue

            self.analyzed_files.append(py_file)
            try:
                self.enhanced_analyzer.analyze_file(py_file)
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        self.quality_issues = self.enhanced_analyzer.quality_issues
        self.issues_count = sum(len(issues) for issues in self.quality_issues.values())

        for category, issues in self.quality_issues.items():
            for issue in issues:
                if isinstance(issue, dict) and 'file_path' in issue:
                    file_path = issue['file_path']
                    self.issues_by_file[file_path].append({
                        'category': category,
                        'description': issue.get('description', 'Unknown issue'),
                        'line': issue.get('line', 'Unknown')
                    })
                    self.code_smells_by_category[category].append(issue)

        self.dependency_analyzer.analyze_directory(self.target_dir)
        self.entry_points = self.dependency_analyzer.get_entry_points()
        self.core_components = self.dependency_analyzer.get_core_components()
        
        self.complexity_metrics = {
            'complex_functions': self.dependency_analyzer.complex_functions,
            'thresholds': self.dependency_analyzer.QUALITY_METRICS
        }

        print(f"Analysis complete! Found {self.issues_count} issues in {len(self.analyzed_files)} files.")

    def generate_report(self) -> str:
        sections = []
        
        sections.append(f"# Treeline Code Analysis Report\n")
        sections.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append(f"**Project:** {self.target_dir.absolute()}")
        sections.append(f"**Files Analyzed:** {len(self.analyzed_files)}")
        sections.append(f"**Issues Found:** {self.issues_count}\n")
        
        sections.append("## Quality Issues Overview\n")
        
        if self.issues_count > 0:
            sections.append("| Category | Count |")
            sections.append("| --- | ---: |")
            for category, issues in self.code_smells_by_category.items():
                sections.append(f"| {category.title()} | {len(issues)} |")
        else:
            sections.append("No quality issues found. Great job!")
        
        security_issues = self.code_smells_by_category.get('security', [])
        sql_injection_issues = [
            issue for category, issues in self.code_smells_by_category.items()
            for issue in issues
            if isinstance(issue, dict) and 
            issue.get('description', '').lower().find('sql injection') != -1
        ]
        
        if security_issues or sql_injection_issues:
            sections.append("\n## Security Issues\n")
            
            if security_issues:
                sections.append("### General Security Issues\n")
                for issue in security_issues:
                    if isinstance(issue, dict):
                        file_path = issue.get('file_path', 'Unknown')
                        rel_path = Path(file_path).relative_to(self.target_dir) if Path(file_path).is_absolute() else file_path
                        line = issue.get('line', 'Unknown')
                        description = issue.get('description', 'Unknown issue')
                        
                        sections.append(f"- **{rel_path}:{line}**: {description}")
            
            if sql_injection_issues:
                sections.append("\n### SQL Injection Vulnerabilities\n")
                for issue in sql_injection_issues:
                    if isinstance(issue, dict):
                        file_path = issue.get('file_path', 'Unknown')
                        rel_path = Path(file_path).relative_to(self.target_dir) if Path(file_path).is_absolute() else file_path
                        line = issue.get('line', 'Unknown')
                        description = issue.get('description', 'Unknown issue')
                        
                        sections.append(f"- **{rel_path}:{line}**: {description}")
        
        sections.append("\n## Complexity Hotspots\n")
        
        if self.complexity_metrics['complex_functions']:
            sections.append("| Module | Function | Complexity |")
            sections.append("| --- | --- | ---: |")
            
            threshold = self.complexity_metrics['thresholds']['MAX_CYCLOMATIC_COMPLEXITY']
            
            for module, func, complexity in sorted(
                self.complexity_metrics['complex_functions'], 
                key=lambda x: x[2], 
                reverse=True
            )[:10]:
                sections.append(f"| {module} | {func} | {complexity} |")
                
            if len(self.complexity_metrics['complex_functions']) > 10:
                sections.append(f"\n*...and {len(self.complexity_metrics['complex_functions']) - 10} more complex functions*")
        else:
            sections.append("No complex functions found. Great job!")
            
        sections.append("\n## Top Issues by File\n")
        
        if self.issues_by_file:
            top_files = sorted(
                self.issues_by_file.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
            
            for file_path, issues in top_files:
                rel_path = Path(file_path).relative_to(self.target_dir) if Path(file_path).is_absolute() else file_path
                sections.append(f"### {rel_path} ({len(issues)} issues)\n")
                
                issues_by_category = defaultdict(list)
                for issue in issues:
                    issues_by_category[issue['category']].append(issue)
                    
                for category, cat_issues in issues_by_category.items():
                    sections.append(f"**{category.title()}** ({len(cat_issues)})\n")
                    
                    for issue in cat_issues[:3]:
                        line_info = f" (Line {issue['line']})" if issue['line'] != 'Unknown' else ""
                        sections.append(f"- {issue['description']}{line_info}")
                    
                    if len(cat_issues) > 3:
                        sections.append(f"- *...and {len(cat_issues) - 3} more {category} issues*")
                    
                    sections.append("")
                    
            if len(self.issues_by_file) > 5:
                sections.append(f"\n*...and {len(self.issues_by_file) - 5} more files with issues*")
        else:
            sections.append("No quality issues found. Great job!")
            
        sections.append("\n## Core Components\n")
        
        if self.core_components:
            sections.append("| Component | Incoming | Outgoing |")
            sections.append("| --- | ---: | ---: |")
            for comp in self.core_components:
                sections.append(f"| {comp['name']} | {comp['incoming']} | {comp['outgoing']} |")
        else:
            sections.append("No core components identified.")
            
        sections.append("\n## Entry Points\n")
        
        if self.entry_points:
            for ep in self.entry_points:
                sections.append(f"- {ep}")
        else:
            sections.append("No entry points identified.")
        
        sections.append("\n---\n")
        sections.append("Report generated by Treeline")
        
        return "\n".join(sections)

    def save_report(self, filename: str = None) -> Path:
        content = self.generate_report()
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"treeline_report_{timestamp}.md"
        
        output_path = self.output_dir / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Report saved to {output_path}")
        return output_path

    def _should_analyze_file(self, file_path: Path) -> bool:
        if any(p in str(file_path) for p in ["venv", "site-packages", "__pycache__", ".git"]):
            return False
            
        return True
