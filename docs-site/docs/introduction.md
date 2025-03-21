# Introduction

Treeline is a powerful code analysis and visualization tool designed for Python codebases. It combines code-flow analysis with quality metrics generation, offering developers actionable insights through a command-line interface (CLI) and an interactive web interface.

## Purpose

Treeline helps developers:
- Understand the structure and dependencies of their Python codebase.
- Identify code quality issues, such as complexity, code smells, and security vulnerabilities.
- Visualize relationships between modules, classes, and functions.
- Generate detailed reports for further analysis.

## Key Features

- **Code Flow Analysis**: Maps dependencies and entry points in your codebase.
- **Quality Metrics**: Detects complex code, unused imports, duplication, and potential security issues like SQL injection.
- **CLI**: Offers commands to analyze, configure, and report on your code.
- **Web Interface**: Provides an interactive visualization of your codebase, powered by React and D3.js, served via FastAPI.
- **Customizable Configuration**: Adjust analysis thresholds using a JSON configuration file.

Treeline is ideal for developers seeking to improve code maintainability and understand large or unfamiliar projects.