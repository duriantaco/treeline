# treeline/utils/report.py
import re
from typing import Dict, List


class ReportGenerator:
    @staticmethod
    def process_markdown(content: str) -> str:
        """Process markdown content with all the regex replacements"""
        # convert mermaid blocks
        content = re.sub(
            r"```mermaid\n(.*?)\n```",
            lambda m: f'<div class="mermaid">\n{m.group(1)}\n</div>',
            content,
            flags=re.DOTALL,
        )

        # cnvert headers
        for i in range(6, 0, -1):
            pattern = f"({'#' * i})\\s+(.+)"
            content = re.sub(pattern, f"<h{i}>\\2</h{i}>", content, flags=re.MULTILINE)

        # convert list items
        content = re.sub(r"^-\s+(.+)", r"<li>\1</li>", content, flags=re.MULTILINE)

        content = re.sub(
            r"(<li>.*?</li>\n)+", r"<ul>\g<0></ul>", content, flags=re.DOTALL
        )
        # convert code blks
        content = re.sub(
            r"```\n(.*?)\n```", r"<pre><code>\1</code></pre>", content, flags=re.DOTALL
        )

        # convert links
        content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', content)

        content = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", content)
        content = re.sub(r"\*([^\*]+)\*", r"<em>\1</em>", content)

        return content

    @classmethod
    def generate_report_data(
        cls,
        tree_str: List[str],
        complex_functions: List[tuple],
        module_metrics: Dict,
        quality_metrics: Dict,
        mermaid_diagrams: Dict,
    ) -> Dict:
        """Generate complete report data structure"""
        return {
            "structure": tree_str,
            "complexity": {
                "functions": complex_functions,
                "thresholds": quality_metrics,
            },
            "metrics": module_metrics,
            "diagrams": mermaid_diagrams,
        }

    @classmethod
    def convert_to_html(cls, report_data: Dict) -> str:
        """Convert report data to HTML content"""
        md_content = []

        md_content.append("# Project Analysis Report\n")

        md_content.append("[Open Interactive Visualization](./visualization)\n")

        md_content.append("## Directory Structure\n")
        md_content.append("```")
        md_content.extend(report_data["structure"])
        md_content.append("```\n")

        md_content.append("## Complexity Hotspots\n")
        if report_data["complexity"]["functions"]:
            for module, func, complexity in sorted(
                report_data["complexity"]["functions"], key=lambda x: x[2], reverse=True
            ):
                md_content.append(f"### {func}")
                md_content.append(f"- **Module**: {module}")
                threshold = report_data["complexity"]["thresholds"][
                    "MAX_CYCLOMATIC_COMPLEXITY"
                ]
                complexity_str = str(complexity)
                if complexity > threshold:
                    complexity_str = f"<span style='color: red'>{complexity_str}</span>"
                md_content.append(f"- **Complexity**: {complexity_str}\n")
        else:
            md_content.append("*No complex functions found.*\n")

        if report_data["diagrams"]:
            md_content.append("## Module Dependencies\n")
            md_content.append("```mermaid")
            md_content.append(report_data["diagrams"]["overview"])
            md_content.append("```\n")

        return cls.process_markdown("\n".join(md_content))
