# What Treeline Tracks and Analyzes
Treeline is designed to provide deep insights into your Python codebase by tracking and analyzing three key areas: dependency mapping, code quality metrics, and structural insights. Here's a breakdown of what specific elements are tracked in each area:

## How Treeline Works
Treeline uses Abstract Syntax Tree (AST) parsing to analyze your Python code. This method ensures accurate insights by examining the code’s structure without executing it, making the analysis both safe and reliable.

It maps dependencies by tracking:  
- **Imports**: Connections between modules.  
- **Calls**: Function and method invocations.  
- **Classes**: Inheritance and composition relationships.

## Dependency Mapping
Treeline examines how different parts of your code are interconnected:

* Module Imports: Tracks which modules import others, revealing dependency relationships and helping identify potential issues like circular imports.

    - Interpretation: 
        * A module with many imports might be overly dependent and harder to maintain.
        * Circular imports (e.g., Module A imports Module B, and vice versa) are problematic and should be flagged.

    - Suggested Actions:
        * Reduce dependencies by splitting large modules.
        * Refactor to eliminate circular imports.

* Function Calls: Maps out which functions call others, both within the same module and across different modules, to show the flow of execution.

    - Interpretation: 
        * Functions with many callers are likely central to your logic and sensitive to modifications.
        * Functions calling many others might be overly complex.

    - Suggested Actions:
        * Simplify complex functions by breaking them into smaller units.

* Class Relationships: Identifies class hierarchies (e.g., inheritance) and tracks method calls between classes to highlight object-oriented dependencies.

    - Interpretation:
        * Deep inheritance (many levels) suggests over-abstraction.
        * Classes with many dependencies may need refactoring.
    
    - Suggested Actions:
        * Flatten deep inheritance trees where possible.
        * Reduce class dependencies to improve modularity.

## Quality Metrics
Treeline evaluates your code to ensure it’s clean, efficient, and secure by tracking:

* Complexity Analysis: Measures cyclomatic complexity to flag functions or methods that are too intricate, making them hard to test or maintain.

    - Interpretation:
        * A score above 10 often indicates a function is too complex.
        * Complex code is harder to understand and maintain.

    - Suggested Actions:
        * Break complex functions into smaller, simpler ones.
        * Reduce conditional branching (e.g., if/else statements).

* Code Smell Detection: Identifies common issues like long functions, excessive parameters, or deep nesting, which suggest areas for improvement.

    - Interpretation:
        * Functions over 50 lines are typically too long.
        * More than 5 parameters suggest a need for restructuring.
        * Nesting deeper than 4 levels reduces clarity.
    - Suggested Actions:
        * Split long functions into smaller pieces.
        * Use parameter objects or defaults for excessive parameters.
        * Flatten nested logic with early returns or helper functions.

* Unused Code Identification: Detects unused imports and functions that can be removed to declutter your codebase.

    - Interpretation
        * Unused imports can be safely removed.
        * Unused functions may indicate outdated or redundant code.
    - Suggested Actions:
        * Delete unused imports and functions to streamline your codebase.

* Duplication Detection: Finds repeated code blocks that could be consolidated into reusable functions or methods.

    - Interpretation:
        * Repeated code suggests opportunities for reuse.
    - Suggested Actions:
        * Refactor duplicates into reusable functions or methods.

* Security Vulnerability Scanning: Checks for risks such as SQL injection vulnerabilities, hardcoded credentials, or use of insecure functions.

    - Interpretation:
        * SQL injection risks need urgent fixes.
        * Hardcoded credentials indicate poor security practices.
    - Suggested Actions:
        * Use parameterized queries for SQL.
        * Move credentials to environment variables or secure storage.

## Structural Insights
Treeline provides a big-picture view of your codebase’s architecture:

* Entry Point Identification: Detects starting points like main functions, CLI commands, or API routes, which are key to understanding how your application runs.
* Core Component Detection: Highlights modules or functions with many dependencies (high connectivity), indicating central pieces of your application.
* Code Structure Visualization: Creates a visual map of your codebase’s structure, accessible via the web interface, to simplify comprehension of complex projects.

## Accessing the Analysis
Users can explore what Treeline tracks through two main interfaces:

### CLI Commands:
* `treeline analyze`: Summarizes dependencies and entry points.
* `treeline quality`: Highlights code quality issues like complexity or smells.
* `treeline report`: Generates a detailed report (in Markdown or JSON) covering all tracked aspects.

### Web Interface:
Run `treeline serve` to launch an interactive visualization at `http://localhost:8000`. Here, you can explore dependency graphs, review metrics, and spot issues visually.