# Treeline Code Analysis Report

**Generated:** 2025-03-04 16:26:08
**Project:** /Users/oha/treeline
**Files Analyzed:** 39
**Issues Found:** 724

## Quality Issues Overview

| Category | Count |
| --- | ---: |
| Code_Smells | 483 |
| Security | 8 |
| Style | 186 |
| Complexity | 47 |

## Security Issues

### General Security Issues

- **tests/test_checkers.py:97**: Possible hardcoded credential
- **tests/test_integration.py:72**: Possible hardcoded credential
- **tests/do_not_use/test_problematic_code.py:39**: Possible hardcoded credential
- **tests/do_not_use/test_problematic_code.py:42**: Possible hardcoded credential
- **treeline/checkers/security.py:17**: Possible hardcoded credential
- **treeline/checkers/security.py:17**: Possible hardcoded credential
- **treeline/checkers/security.py:17**: Possible hardcoded credential
- **treeline/api/app.py:55**: Possible hardcoded credential

## Complexity Hotspots

| Module | Function | Complexity |
| --- | --- | ---: |
| tests.test_integration | simulate_visualization | 37 |
| treeline.dependency_analyzer | get_graph_data_with_quality | 30 |
| treeline.utils.report | generate_report | 26 |
| treeline.type_checker | validate | 22 |
| tests.do_not_use.test_problematic_code | process_data | 21 |
| treeline.dependency_analyzer | get_graph_data | 17 |
| treeline.enhanced_analyzer | _add_file_issues_to_elements | 16 |
| treeline.dependency_analyzer | _analyze_module | 15 |
| treeline.core | generate_tree | 15 |
| treeline.core | format_structure | 13 |

*...and 5 more complex functions*

## Top Issues by File

### treeline/dependency_analyzer.py (97 issues)

**Code_Smells** (62)

- Magic number detected (Line 176)
- Magic number detected (Line 203)
- Magic number detected (Line 76)
- *...and 59 more code_smells issues*

**Style** (27)

- Line is too long (Line 40)
- Line is too long (Line 41)
- Line is too long (Line 46)
- *...and 24 more style issues*

**Complexity** (8)

- High cyclomatic complexity (90 > 10) (Line 16)
- High cognitive complexity (247 > 15) (Line 16)
- High cyclomatic complexity (15 > 10) (Line 112)
- *...and 5 more complexity issues*

### tests/test_integration.py (89 issues)

**Code_Smells** (67)

- Magic number detected (Line 108)
- Magic number detected (Line 108)
- Magic number detected (Line 238)
- *...and 64 more code_smells issues*

**Security** (1)

- Possible hardcoded credential (Line 72)

**Style** (17)

- Line is too long (Line 96)
- Line is too long (Line 104)
- Line is too long (Line 242)
- *...and 14 more style issues*

**Complexity** (4)

- High cyclomatic complexity (11 > 10) (Line 200)
- High cognitive complexity (20 > 15) (Line 200)
- High cyclomatic complexity (37 > 10) (Line 278)
- *...and 1 more complexity issues*

### treeline/api/app.py (75 issues)

**Code_Smells** (50)

- Magic number detected (Line 32)
- Magic number detected (Line 33)
- Magic number detected (Line 518)
- *...and 47 more code_smells issues*

**Security** (1)

- Possible hardcoded credential (Line 55)

**Style** (24)

- File has 528 lines (over 500) (Line None)
- Line is too long (Line 91)
- Line is too long (Line 122)
- *...and 21 more style issues*

### tests/do_not_use/test_problematic_code.py (73 issues)

**Code_Smells** (56)

- Magic number detected (Line 24)
- Magic number detected (Line 28)
- Magic number detected (Line 49)
- *...and 53 more code_smells issues*

**Security** (2)

- Possible hardcoded credential (Line 39)
- Possible hardcoded credential (Line 42)

**Style** (13)

- Line is too long (Line 60)
- Line is too long (Line 66)
- Line is too long (Line 83)
- *...and 10 more style issues*

**Complexity** (2)

- High cyclomatic complexity (21 > 10) (Line 71)
- High cognitive complexity (116 > 15) (Line 71)

### treeline/utils/report.py (50 issues)

**Code_Smells** (29)

- Magic number detected (Line 26)
- Magic number detected (Line 214)
- Magic number detected (Line 77)
- *...and 26 more code_smells issues*

**Style** (17)

- Line is too long (Line 42)
- Line is too long (Line 50)
- Line is too long (Line 64)
- *...and 14 more style issues*

**Complexity** (4)

- High cyclomatic complexity (36 > 10) (Line 6)
- High cognitive complexity (67 > 15) (Line 6)
- High cyclomatic complexity (26 > 10) (Line 66)
- *...and 1 more complexity issues*


*...and 26 more files with issues*

## Core Components

| Component | Incoming | Outgoing |
| --- | ---: | ---: |
| treeline.core | 5 | 13 |
| treeline.enhanced_analyzer | 5 | 12 |
| treeline.dependency_analyzer | 5 | 7 |
| treeline.models.enhanced_analyzer | 6 | 3 |

## Entry Points

- tests.test_special_char
- tests.test_empty_dir
- tests.test_core
- tests.test_checkers
- tests.test_treeline
- tests.test_integration
- tests.test_nested_dir
- tests.do_not_use.test_problematic_code
- tests.do_not_use.super_long_code
- treeline.analyzer
- treeline.__init__
- treeline.cli
- treeline.__main__
- treeline.optimization.graph
- treeline.utils.config
- treeline.utils.__init__
- treeline.models.__init__
- treeline.api.__init__
- docs.conf

---

Report generated by Treeline