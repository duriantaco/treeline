# import subprocess
# import json
# from datetime import datetime
# from pathlib import Path
# from typing import Dict, List, Optional, Tuple, Union
# from dataclasses import dataclass
# from tempfile import NamedTemporaryFile
# import re
# from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

# @dataclass
# class CommitInfo:
#     """Information about a specific commit."""
#     hash: str
#     author: str
#     date: datetime
#     message: str

# @dataclass
# class TemporalMetrics:
#     """Metrics tracked over time for a file."""
#     commit: CommitInfo
#     metrics: Dict[str, Union[int, float]]
#     complexity: int
#     maintainability_index: float
#     cognitive_complexity: int

#     @property
#     def health_score(self) -> float:
#         """Calculate overall health score based on metrics."""
#         complexity_score = max(0, 1 - (self.complexity / 50))
#         maintainability_score = self.maintainability_index / 100
#         cognitive_score = max(0, 1 - (self.cognitive_complexity / 30))

#         return (complexity_score * 0.3 +
#                 maintainability_score * 0.4 +
#                 cognitive_score * 0.3) * 100

# class GitTemporalAnalyzer:
#     """Analyzes code health changes over time using git history."""

#     def __init__(self, repo_path: str):
#         """Initialize analyzer with repository path."""
#         self.repo_path = Path(repo_path).resolve()
#         if not self.repo_path.exists():
#             raise ValueError(f"Repository path does not exist: {self.repo_path}")

#         # Verify it's a git repository
#         self._run_git_command(['rev-parse', '--git-dir'])

#         self.enhanced_analyzer = EnhancedCodeAnalyzer(show_params=True)

#     def _run_git_command(self,
#                         command: List[str],
#                         capture_output: bool = True) -> Optional[str]:
#         """Run a git command safely and return its output."""
#         try:
#             full_command = ['git'] + command
#             result = subprocess.run(
#                 full_command,
#                 cwd=self.repo_path,
#                 capture_output=capture_output,
#                 text=True,
#                 check=True
#             )
#             return result.stdout.strip() if capture_output else None
#         except subprocess.CalledProcessError as e:
#             error_msg = f"Git command failed: {' '.join(full_command)}\n{e.stderr}"
#             raise RuntimeError(error_msg) from e
#         except Exception as e:
#             raise RuntimeError(f"Error running git command: {e}") from e

#     def _parse_commit_info(self, log_entry: str) -> CommitInfo:
#         """Parse git log entry into CommitInfo object."""
#         # Format: hash~~~author~~~timestamp~~~message
#         try:
#             hash_val, author, timestamp, message = log_entry.split('~~~')
#             return CommitInfo(
#                 hash=hash_val.strip(),
#                 author=author.strip(),
#                 date=datetime.fromtimestamp(int(timestamp.strip())),
#                 message=message.strip()
#             )
#         except ValueError as e:
#             raise ValueError(f"Invalid git log format: {log_entry}") from e

#     def get_file_history(self,
#                         file_path: str,
#                         start_date: Optional[datetime] = None,
#                         end_date: Optional[datetime] = None) -> List[CommitInfo]:
#         """Get commit history for a specific file."""
#         file_path = Path(file_path).resolve().relative_to(self.repo_path)

#         log_command = [
#             'log',
#             '--format=%H~~~%an~~~%at~~~%s',  # Custom format for easy parsing
#             '--follow',  # Follow file renames
#             str(file_path)
#         ]

#         if start_date:
#             log_command.extend(['--since', start_date.strftime('%Y-%m-%d')])
#         if end_date:
#             log_command.extend(['--until', end_date.strftime('%Y-%m-%d')])

#         log_output = self._run_git_command(log_command)
#         if not log_output:
#             return []

#         commits = []
#         for line in log_output.split('\n'):
#             if line.strip():
#                 try:
#                     commits.append(self._parse_commit_info(line))
#                 except ValueError as e:
#                     print(f"Warning: Skipping invalid commit log entry: {e}")
#                     continue

#         return commits

#     def get_file_content_at_commit(self,
#                                  file_path: str,
#                                  commit_hash: str) -> Optional[str]:
#         """Get content of a file at a specific commit."""
#         file_path = Path(file_path).resolve().relative_to(self.repo_path)

#         try:
#             content = self._run_git_command([
#                 'show',
#                 f'{commit_hash}:{file_path}'
#             ])
#             return content
#         except RuntimeError:
#             return None

#     def analyze_file_history(self,
#                            file_path: str,
#                            start_date: Optional[datetime] = None,
#                            end_date: Optional[datetime] = None) -> List[TemporalMetrics]:
#         """Analyze a file's health metrics through its git history."""
#         commits = self.get_file_history(file_path, start_date, end_date)
#         metrics_history = []

#         for commit in commits:
#             content = self.get_file_content_at_commit(file_path, commit.hash)
#             if not content:
#                 continue

#             # Use a temporary file for analysis
#             with NamedTemporaryFile(mode='w', suffix='.py', delete=True) as temp_file:
#                 temp_file.write(content)
#                 temp_file.flush()

#                 try:
#                     # Analyze the historical version
#                     analysis_results = self.enhanced_analyzer.analyze_file(Path(temp_file.name))

#                     # Extract metrics
#                     metrics = self._extract_metrics(analysis_results)

#                     # Create temporal metrics record
#                     temporal_metrics = TemporalMetrics(
#                         commit=commit,
#                         metrics=metrics,
#                         complexity=metrics.get('complexity', 0),
#                         maintainability_index=metrics.get('maintainability_index', 0.0),
#                         cognitive_complexity=metrics.get('cognitive_complexity', 0)
#                     )

#                     metrics_history.append(temporal_metrics)

#                 except Exception as e:
#                     print(f"Warning: Error analyzing commit {commit.hash}: {e}")
#                     continue

#         return metrics_history

#     def _extract_metrics(self, analysis_results: List[Dict]) -> Dict:
#         """Extract relevant metrics from analysis results."""
#         combined_metrics = {}

#         for result in analysis_results:
#             if 'metrics' in result:
#                 combined_metrics.update(result['metrics'])

#         return combined_metrics

#     def calculate_metric_trends(self,
#                               metrics_history: List[TemporalMetrics]) -> Dict[str, float]:
#         """Calculate trends for different metrics over time."""
#         if not metrics_history or len(metrics_history) < 2:
#             return {
#                 'complexity_trend': 0.0,
#                 'maintainability_trend': 0.0,
#                 'cognitive_complexity_trend': 0.0,
#                 'health_score_trend': 0.0
#             }

#         trends = {}

#         # Calculate trends for each metric
#         complexity_values = [m.complexity for m in metrics_history]
#         maintainability_values = [m.maintainability_index for m in metrics_history]
#         cognitive_values = [m.cognitive_complexity for m in metrics_history]
#         health_values = [m.health_score for m in metrics_history]

#         trends['complexity_trend'] = self._calculate_trend(complexity_values)
#         trends['maintainability_trend'] = self._calculate_trend(maintainability_values)
#         trends['cognitive_complexity_trend'] = self._calculate_trend(cognitive_values)
#         trends['health_score_trend'] = self._calculate_trend(health_values)

#         return trends

#     def _calculate_trend(self, values: List[float]) -> float:
#         """Calculate trend direction and magnitude using linear regression."""
#         n = len(values)
#         x = list(range(n))
#         x_mean = sum(x) / n
#         y_mean = sum(values) / n

#         numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
#         denominator = sum((xi - x_mean) ** 2 for xi in x)

#         return numerator / denominator if denominator != 0 else 0.0

#     def identify_significant_changes(self,
#                                   history: List[TemporalMetrics],
#                                   complexity_threshold: int = 5,
#                                   maintainability_threshold: float = 10.0) -> List[Dict]:
#         """Identify commits with significant metric changes."""
#         significant_changes = []

#         for i in range(1, len(history)):
#             prev, curr = history[i-1], history[i]

#             complexity_change = curr.complexity - prev.complexity
#             maintainability_change = curr.maintainability_index - prev.maintainability_index

#             if (abs(complexity_change) > complexity_threshold or
#                 abs(maintainability_change) > maintainability_threshold):

#                 significant_changes.append({
#                     'commit_hash': curr.commit.hash,
#                     'date': curr.commit.date.isoformat(),
#                     'author': curr.commit.author,
#                     'message': curr.commit.message,
#                     'changes': {
#                         'complexity_change': complexity_change,
#                         'maintainability_change': maintainability_change,
#                         'cognitive_complexity_change':
#                             curr.cognitive_complexity - prev.cognitive_complexity,
#                         'health_score_change':
#                             curr.health_score - prev.health_score
#                     }
#                 })

#         return significant_changes

#     def generate_analysis_report(self,
#                                file_path: str,
#                                start_date: Optional[datetime] = None,
#                                end_date: Optional[datetime] = None) -> Dict:
#         """Generate a comprehensive analysis report for a file."""
#         metrics_history = self.analyze_file_history(file_path, start_date, end_date)

#         if not metrics_history:
#             return {
#                 'error': 'No metrics history available for analysis',
#                 'file_path': str(file_path)
#             }

#         trends = self.calculate_metric_trends(metrics_history)
#         significant_changes = self.identify_significant_changes(metrics_history)

#         latest = metrics_history[0]
#         oldest = metrics_history[-1]

#         return {
#             'file_path': str(file_path),
#             'analysis_period': {
#                 'start': oldest.commit.date.isoformat(),
#                 'end': latest.commit.date.isoformat()
#             },
#             'commit_count': len(metrics_history),
#             'current_health': {
#                 'complexity': latest.complexity,
#                 'maintainability_index': latest.maintainability_index,
#                 'cognitive_complexity': latest.cognitive_complexity,
#                 'health_score': latest.health_score
#             },
#             'trends': trends,
#             'significant_changes': significant_changes,
#             'contributors': self._analyze_contributors(metrics_history)
#         }

#     def _analyze_contributors(self, history: List[TemporalMetrics]) -> List[Dict]:
#         """Analyze contribution patterns and their impact on code health."""
#         contributor_stats = {}

#         for metrics in history:
#             author = metrics.commit.author
#             if author not in contributor_stats:
#                 contributor_stats[author] = {
#                     'commit_count': 0,
#                     'complexity_changes': [],
#                     'maintainability_changes': [],
#                     'cognitive_changes': []
#                 }

#             stats = contributor_stats[author]
#             stats['commit_count'] += 1
#             stats['complexity_changes'].append(metrics.complexity)
#             stats['maintainability_changes'].append(metrics.maintainability_index)
#             stats['cognitive_changes'].append(metrics.cognitive_complexity)

#         # Calculate impact metrics for each contributor
#         contributor_impact = []
#         for author, stats in contributor_stats.items():
#             impact = {
#                 'author': author,
#                 'commit_count': stats['commit_count'],
#                 'avg_complexity_change': (
#                     sum(stats['complexity_changes']) / len(stats['complexity_changes'])
#                 ),
#                 'avg_maintainability_change': (
#                     sum(stats['maintainability_changes']) /
#                     len(stats['maintainability_changes'])
#                 ),
#                 'avg_cognitive_change': (
#                     sum(stats['cognitive_changes']) / len(stats['cognitive_changes'])
#                 )
#             }
#             contributor_impact.append(impact)

#         return sorted(contributor_impact, key=lambda x: x['commit_count'], reverse=True)
