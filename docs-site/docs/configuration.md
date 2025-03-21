# Configuration

Treeline uses a JSON configuration file (`treeline.json` by default) to customize analysis settings.

## Default Configuration

Key settings include:
- `MAX_PARAMS`: Max allowed function parameters (default: 5).
- `MAX_FUNCTION_LINES`: Max lines in a function (default: 50).
- `MAX_CLASS_LINES`: Max lines in a class (default: 300).
- `MAX_LINE_LENGTH`: Max line length (default: 100).
- `MAX_NESTED_DEPTH`: Max nesting depth (default: 4).

View the full configuration:
```bash
treeline config show
```

## Customizing Configuration

1. Create a Default File:

```bash
treeline config init
```
* Saves to `./treeline.json` (or specify `--path`).

2. Modify Settings: Edit `treeline.json` directly, or use the CLI:

```bash
treeline config set MAX_LINE_LENGTH 120
```

3. Apply Custom Configuration: Pass the file to commands:

```bash
treeline analyze . --config ./my_config.json
```