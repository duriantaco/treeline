import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.models.dependency_analyzer import GraphData, Node


class DiffVisualizer:
    """Visualizes structural differences between different versions of Python code."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.dep_analyzer = ModuleDependencyAnalyzer()

    def _serialize_graph_data(self, graph: GraphData) -> Dict:
        """Convert a GraphData object to a serializable dictionary"""
        return {
            "nodes": [self._serialize_node(n) for n in graph.nodes],
            "links": [self._serialize_link(link) for link in graph.links],
        }

    def _serialize_node(self, node: Node) -> Dict:
        """Convert a Node object to a serializable dictionary"""
        return {
            "id": str(node.id),
            "name": str(node.name),
            "type": str(node.type),
            "group": getattr(node, "group", 1),
            "size": getattr(node, "size", 1),
        }

    def _serialize_link(self, link: Dict) -> Dict:
        """Convert a link dictionary to a serializable format"""
        return {
            "source": (
                str(link["source"])
                if isinstance(link["source"], (str, int))
                else str(link["source"].id)
            ),
            "target": (
                str(link["target"])
                if isinstance(link["target"], (str, int))
                else str(link["target"].id)
            ),
            "type": str(link.get("type", "default")),
            "value": link.get("value", 1),
        }

    def _node_was_modified_serial(self, before: Dict, after: Dict) -> bool:
        """Check if a serialized node's important properties changed"""
        return (
            before["name"] != after["name"]
            or before["type"] != after["type"]
            or before.get("group") != after.get("group")
        )

    def _get_node_changes_serial(self, before: Dict, after: Dict) -> Dict:
        """Get detailed changes for modified serialized nodes"""
        changes = {}
        for key in ["name", "type", "group"]:
            if before.get(key) != after.get(key):
                changes[key] = {"before": before.get(key), "after": after.get(key)}
        return changes

    def _run_git_command(self, *args) -> str:
        """Run a git command with error handling"""
        try:
            print(f"DEBUG: Running git command: git {' '.join(args)}")
            result = subprocess.run(
                ["git"] + list(args),
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
                encoding="utf-8",
                timeout=30,
            )
            print(f"DEBUG: Git command output: {result.stdout[:100]}...")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print("DEBUG: Git command timed out")
            raise RuntimeError("Git command timed out")
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Git command failed: {e.stderr}")
            raise RuntimeError(f"Git command failed: {e.stderr}")
        except Exception as e:
            print(f"DEBUG: Unexpected error: {str(e)}")
            raise RuntimeError(f"Unexpected error: {str(e)}")

    def _is_git_repo(self) -> bool:
        try:
            self._run_git_command("rev-parse", "--is-inside-work-tree")
            return True
        except RuntimeError:
            return False

    def _commit_exists(self, commit_sha: str) -> bool:
        try:
            self._run_git_command("cat-file", "-e", commit_sha)
            return True
        except RuntimeError:
            return False

    def _analyze_commit(self, commit_sha: str) -> Dict:
        """Analyze a specific commit and return serializable data"""
        if not self._commit_exists(commit_sha):
            raise ValueError(f"Commit {commit_sha} not found")

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            try:
                self._run_git_command("worktree", "add", str(temp_path), commit_sha)
                self.dep_analyzer.analyze_directory(temp_path)
                html_viz = self.dep_analyzer.generate_html_visualization()
                viz_data = json.loads(html_viz.split("const data = ")[1].split(";")[0])

                return {
                    "nodes": [
                        {"id": n["id"], "name": n["name"], "type": n["type"]}
                        for n in viz_data["nodes"]
                    ],
                    "links": [
                        {
                            "source": link["source"],
                            "target": link["target"],
                            "type": link["type"],
                        }
                        for link in viz_data["links"]
                    ],
                }
            finally:
                self._run_git_command("worktree", "remove", "-f", str(temp_path))

    def _compute_changes(self, before_data: Dict, after_data: Dict) -> Dict:
        """Compute the differences between two dependency graphs"""

        def node_key(node):
            return f"{node['id']}-{node['name']}-{node['type']}"

        def link_key(link):
            return f"{link['source']}-{link['target']}-{link['type']}"

        before_node_keys = {node_key(n) for n in before_data["nodes"]}
        after_node_keys = {node_key(n) for n in after_data["nodes"]}
        before_link_keys = {link_key(link) for link in before_data["links"]}
        after_link_keys = {link_key(link) for link in after_data["links"]}

        changes = {
            "added": {
                "nodes": [
                    n
                    for n in after_data["nodes"]
                    if node_key(n) not in before_node_keys
                ],
                "links": [
                    link
                    for link in after_data["links"]
                    if link_key(link) not in before_link_keys
                ],
            },
            "removed": {
                "nodes": [
                    n
                    for n in before_data["nodes"]
                    if node_key(n) not in after_node_keys
                ],
                "links": [
                    link
                    for link in before_data["links"]
                    if link_key(link) not in after_link_keys
                ],
            },
            "modified": [],
        }

        return changes

    def generate_structural_diff(self, before_commit: str, after_commit: str) -> str:
        """Generate a visual diff between two commits"""
        if not self._is_git_repo():
            raise ValueError("Not a git repository")

        before_data = self._analyze_commit(before_commit)
        after_data = self._analyze_commit(after_commit)
        changes = self._compute_changes(before_data, after_data)

        after_data["commits"] = {"before": before_commit, "after": after_commit}

        file_diffs = {}
        for node in after_data["nodes"]:
            try:
                file_path = node["name"].replace(".", "/") + ".py"
                print(f"DEBUG: Getting diff for file path: {file_path}")

                diff = self._run_git_command(
                    "diff", "--unified=3", before_commit, after_commit, "--", file_path
                )
                if diff.strip():
                    file_diffs[node["name"]] = diff
                else:
                    print(f"DEBUG: No diff found for {file_path}")
                    file_diffs[node["name"]] = ""
            except Exception as e:
                print(f"DEBUG: Error getting diff for {node['name']}: {str(e)}")
                file_diffs[node["name"]] = f"Error getting diff: {str(e)}"

        print(f"DEBUG: Computed {len(file_diffs)} diffs")
        print(
            "DEBUG: Sample diffs:",
            {k: v[:100] for k, v in list(file_diffs.items())[:3]},
        )

        after_data["file_diffs"] = file_diffs

        for node in after_data["nodes"]:
            if any(n["name"] == node["name"] for n in changes["added"]["nodes"]):
                node["status"] = "added"
            else:
                node["status"] = "unchanged"

        for link in after_data["links"]:
            if any(
                added_link["source"] == link["source"]
                and added_link["target"] == link["target"]
                for added_link in changes["added"]["links"]
            ):
                link["status"] = "added"
            else:
                link["status"] = "unchanged"

        for node in changes["removed"]["nodes"]:
            node["status"] = "removed"
            after_data["nodes"].append(node)

        for link in changes["removed"]["links"]:
            link["status"] = "removed"
            after_data["links"].append(link)

        template = self.dep_analyzer.html_template

        diff_styles = """
            .node-added circle { fill: #22c55e; }  /* Green */
            .node-removed circle { fill: #ef4444; opacity: 0.7; }  /* Red */
            .node-modified circle { fill: #eab308; }  /* Yellow */
            .link-added { stroke: #22c55e; stroke-width: 3px; }
            .link-removed { stroke: #ef4444; stroke-width: 3px; opacity: 0.7; }
            .node-highlighted circle {
                stroke: #3b82f6;
                stroke-width: 3px;
                filter: brightness(1.2);
            }
            .popup-button {
                padding: 8px 16px;
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin: 8px;
                display: none;
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1001;
            }
            .popup {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                z-index: 1000;
                display: none;
                max-width: 80%;
                max-height: 80vh;
                overflow-y: auto;
            }
            .popup.active {
                display: block;
            }
            .popup-close {
                position: absolute;
                right: 10px;
                top: 10px;
                cursor: pointer;
                font-size: 20px;
            }
            .diff-container {
                display: flex;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                font-size: 12px;
                line-height: 1.5;
                tab-size: 2;
            }
            .line-numbers {
                padding: 0 8px;
                text-align: right;
                background: #f6f8fa;
                color: #57606a;
                user-select: none;
                border-right: 1px solid #d0d7de;
            }
            .diff-content {
                padding-left: 10px;
                white-space: pre;
                overflow-x: auto;
                flex-grow: 1;
            }
            .diff-line {
                display: flex;
            }
            .diff-line-add {
                background-color: #e6ffec;
            }
            .diff-line-remove {
                background-color: #ffebe9;
            }
            .diff-header {
                color: #656d76;
                background: #f6f8fa;
            }
            .diff-line-number {
                color: #6e7781;
                width: 40px;
                text-align: right;
                padding-right: 10px;
                user-select: none;
            }
        """
        template = template.replace("</style>", f"{diff_styles}\n</style>")

        original_link_code = """const link = g.append("g")
                    .selectAll("path")
                    .data(data.links)
                    .join("path")
                    .attr("class", d => `link link-${d.type}`)
                    .attr("marker-end", d => `url(#arrow-${d.type})`);"""

        original_node_code = """const node = g.append("g")
                    .selectAll(".node")
                    .data(data.nodes)
                    .join("g")
                    .attr("class", d => `node node-${d.type}`)
                    .call(drag(simulation));"""

        new_link_code = """const link = g.append("g")
                    .selectAll("path")
                    .data(data.links)
                    .join("path")
                    .attr("class", function(d) {
                        return "link link-" + d.type + (d.status ? " link-" + d.status : "");
                    })
                    .attr("marker-end", function(d) {
                        return "url(#arrow-" + d.type + ")";
                    });"""

        new_node_code = """const node = g.append("g")
                    .selectAll(".node")
                    .data(data.nodes)
                    .join("g")
                    .attr("class", function(d) {
                        return "node node-" + d.type + (d.status ? " node-" + d.status : "");
                    })
                    .call(drag(simulation))
                    .on("click", function(event, d) {
                        // Remove highlight from all nodes
                        node.classed("node-highlighted", false);

                        // Add highlight to clicked node
                        d3.select(this).classed("node-highlighted", true);

                        // Update node name
                        document.getElementById("selected-node").textContent = d.name;

                        // Get the pre-computed diff for this node
                        const diffText = data.file_diffs[d.name] || 'No changes found';

                        // Format the diff with colors
                        document.getElementById("git-diff").innerHTML = diffText
                            .split('\\n')
                            .map(line => {
                                if (line.startsWith('+')) {
                                    return '<div style="background-color: #e6ffec; color: #1a7f37;">' + line + '</div>';
                                } else if (line.startsWith('-')) {
                                    return '<div style="background-color: #ffebe9; color: #cf222e;">' + line + '</div>';
                                } else if (line.startsWith('@@')) {
                                    return '<div style="color: #656d76; background: #f6f8fa;">' + line + '</div>';
                                }
                                return '<div>' + line + '</div>';
                            })
                            .join('\\n');

                        // Show the button
                        document.getElementById("popup-button").style.display = "block";
                    });"""

        template = template.replace(original_link_code, new_link_code)
        template = template.replace(original_node_code, new_node_code)

        popup_html = """
            <button id="popup-button" class="popup-button">Show Details</button>
            <div id="popup" class="popup">
                <span class="popup-close">&times;</span>
                <h3>Node Details</h3>
                <p>Selected Node: <span id="selected-node"></span></p>
                <p>Git Diff:</p>
                <pre id="git-diff" style="max-height: 400px; overflow-y: auto; font-family: monospace;"></pre>
            </div>"""

        popup_script = """
            <script>
                document.getElementById("popup-button").addEventListener("click", function() {
                    document.getElementById("popup").classList.add("active");
                });

                document.querySelector(".popup-close").addEventListener("click", function() {
                    document.getElementById("popup").classList.remove("active");
                });

                window.addEventListener("click", function(event) {
                    const popup = document.getElementById("popup");
                    if (event.target === popup) {
                        popup.classList.remove("active");
                    }
                });
            </script>
        """

        change_legend = """
                <div style="margin-top: 16px; border-top: 1px solid #e5e7eb; padding-top: 12px;">
                    <h4 style="margin-top: 0; margin-bottom: 8px;">Changes</h4>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #22c55e;"></div>
                        <span>Added</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ef4444;"></div>
                        <span>Removed</span>
                    </div>
                </div>"""

        legend_end = '</div>\n            <svg id="visualization"></svg>'
        template = template.replace(
            legend_end,
            f'{change_legend}\n{popup_html}\n            </div>\n            <svg id="visualization"></svg>{popup_script}',
        )

        return template.replace("GRAPH_DATA_PLACEHOLDER", json.dumps(after_data))
