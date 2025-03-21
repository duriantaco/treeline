# CLI Usage

Treeline’s command-line interface (CLI) provides a suite of commands to analyze and manage your Python codebase.

Run `treeline --help` to see all available commands

## Overview

* Analyze structural dependencies
* Check code quality
* Generate reports
* Launch a web interface
* Manage configuration


## Commands

### Config
Manage Treeline’s configuration settings.

1. Init
Create a default configuration file (`treeline.json`).

```bash
treeline config init
```

* `--path`: Specify where to save the file (default: `./treeline.json`).

2. Show
```bash
treeline config show
```

* `--path`: Path to a specific configuration file (optional).

3. Set
```bash
treeline config set KEY VALUE
```

* `--path`: Path to save the updated configuration.
* Example: treeline config set `MAX_LINE_LENGTH 120`.

## Serve
Launch the web interface using FastAPI and Uvicorn.

```bash
treeline serve
```

* Starts a server at `http://localhost:8000`.
* No additional setup is needed; the frontend is served automatically.

## Report 
Generate a summary report of analysis results.

```bash
## You can cd to the root of your python codebase and run this 
treeline report
```

* `--output`: Output file name (default: `treeline_report.md`).
* `--json`: Output in JSON format instead of Markdown.