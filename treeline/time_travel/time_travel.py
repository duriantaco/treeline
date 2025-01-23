import json
from pathlib import Path
from typing import Any, Dict


class TimeTravelAnalyzer:
    """
    Provides a simple 'time-travel' / historical analysis of your code structure
    by storing snapshots of indexing results (modules, classes, complexity, etc.)
    so you can compare them at different points in time.
    """

    def __init__(self, snapshot_dir: str = ".treeline_history"):
        """
        Args:
            snapshot_dir: Directory where snapshot JSON files will be stored
        """
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(exist_ok=True)

    def store_snapshot(self, indexer, commit_label: str):
        """
        Store a snapshot of the current index data and complexity stats.

        Args:
            indexer: Your FastIndexer instance with .index, .dependency_graph, etc.
            commit_label: A label or commit SHA identifying this snapshot
        """
        # 1) Basic code structure (IndexEntries)
        # 2) Possibly complexity data or stats if you have them
        # 3) The overall dependency graph
        snapshot_data = {
            "commit_label": commit_label,
            "indexed_elements": {},
            "dependencies": {},
        }

        for entry_hash, entry in indexer.index.items():
            snapshot_data["indexed_elements"][entry_hash] = {
                "name": entry.name,
                "path": entry.path,
                "type": entry.type,
                "dependencies": sorted(list(entry.dependencies)),
                "lines": (entry.line_start, entry.line_end),
            }

        dep_graph_serialized = {}
        for key, deps in indexer.dependency_graph.items():
            dep_graph_serialized[key] = sorted(list(deps))
        snapshot_data["dependencies"] = dep_graph_serialized

        # write snapshot to a JSON file
        snapshot_file = self.snapshot_dir / f"{commit_label}.json"
        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2)

        print(f"[TimeTravel] Snapshot stored -> {snapshot_file}")

    def load_snapshot(self, commit_label: str) -> Dict[str, Any]:
        """
        Load a previously stored snapshot.

        Args:
            commit_label: The label or commit ID for which we have a JSON snapshot

        Returns:
            The deserialized JSON dictionary representing that snapshot
        """
        snapshot_file = self.snapshot_dir / f"{commit_label}.json"
        if not snapshot_file.exists():
            raise FileNotFoundError(
                f"No snapshot found for '{commit_label}' at {snapshot_file}"
            )

        with open(snapshot_file, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)

        return snapshot_data

    def compare_snapshots(self, old_label: str, new_label: str) -> Dict[str, Any]:
        """
        Compare two snapshots to see how the code structure changed (added/removed items, etc.).

        Args:
            old_label: The older snapshot's commit label
            new_label: The newer snapshot's commit label

        Returns:
            A dictionary with keys 'added', 'removed', and 'changed' describing differences.
        """
        old_data = self.load_snapshot(old_label)
        new_data = self.load_snapshot(new_label)

        old_elements = old_data.get("indexed_elements", {})
        new_elements = new_data.get("indexed_elements", {})

        old_keys = set(old_elements.keys())
        new_keys = set(new_elements.keys())

        added = new_keys - old_keys
        removed = old_keys - new_keys
        same = old_keys.intersection(new_keys)

        changed = []
        for k in same:
            if old_elements[k]["dependencies"] != new_elements[k]["dependencies"]:
                changed.append(k)

        results = {
            "added": [(k, new_elements[k]) for k in sorted(added)],
            "removed": [(k, old_elements[k]) for k in sorted(removed)],
            "changed": [(k, old_elements[k], new_elements[k]) for k in changed],
        }

        return results

    def print_comparison_report(self, old_label: str, new_label: str):
        """
        Print a simple console summary of what changed between snapshots.
        """
        diffs = self.compare_snapshots(old_label, new_label)

        print("\n=== Time-Travel Comparison Report ===")
        print(f"Comparing: {old_label} -> {new_label}\n")

        if not diffs["added"] and not diffs["removed"] and not diffs["changed"]:
            print("No differences found.")
            return

        if diffs["added"]:
            print("Newly Added Elements:")
            for elem_hash, elem_data in diffs["added"]:
                print(
                    f"  - {elem_data['type']} '{elem_data['name']}' at {elem_data['path']}"
                )

        if diffs["removed"]:
            print("\nRemoved Elements:")
            for elem_hash, elem_data in diffs["removed"]:
                print(
                    f"  - {elem_data['type']} '{elem_data['name']}' at {elem_data['path']}"
                )

        if diffs["changed"]:
            print("\nChanged Elements (dependencies changed):")
            for elem_hash, (old_elem, new_elem) in [
                (h, (o, n)) for (h, o, n) in diffs["changed"]
            ]:
                print(
                    f"  - {old_elem['type']} '{old_elem['name']}' at {old_elem['path']}"
                )
                print(f"    Old deps: {old_elem['dependencies']}")
                print(f"    New deps: {new_elem['dependencies']}")

        print("====================================\n")
