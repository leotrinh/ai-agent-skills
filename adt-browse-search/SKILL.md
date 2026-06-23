---
name: adt-browse-search
description: "Browse and search SAP ABAP repository via ADT REST API. Fills gaps in adt-mcp-server: search objects/packages, list package contents, read source code, list transports. Use when MCP ADT tools don't support the needed query."
category: sap-abap
keywords: [SAP, ABAP, ADT, packages, search, transport, source, repository]
argument-hint: "[command] [options]"
metadata:
  author: Leo
  version: "1.0.0"
---

# ADT Browse & Search

Bridges capability gaps in `adt-mcp-server` by querying the SAP ADT REST API directly.

## Script

```
~/.claude/skills/adt-browse-search/scripts/adt-client.py
```

Run with: `~\.claude\skills\.venv\Scripts\python.exe ~/.claude/skills/adt-browse-search/scripts/adt-client.py`

Or use the prebuilt binary: `~/.claude/skills/adt-browse-search/bin/adt-client.exe`

## Connection Params (required for all commands)

| Param | Description | Example |
|-------|-------------|---------|
| `--url` | SAP system base URL | `https://host:44300` |
| `--user` | SAP logon user | `LEOS4` |
| `--pwd` | SAP password | `***` |
| `--client` | SAP client (default: `100`) | `100` |
| `--lang` | Logon language (default: `EN`) | `EN` |

## Commands

### `search` — Search objects by name / type / package
```bash
python adt-client.py --url <url> --user <u> --pwd <p> search "Z*" --type PROG/P --package ZPACKAGE --max 50
```
| Arg | Description |
|-----|-------------|
| `query` | Name pattern, e.g. `Z*`, `ZCL_*`, `*` |
| `--type` | Object type: `PROG/P` `CLAS/OC` `INTF/OI` `DEVC/K` `TABL/DT` `FUGR/FF` |
| `--package` | Filter by package name |
| `--author` | Filter by author/responsible user |
| `--max` | Max results (default: 100) |

### `objects` — List all objects in a package
```bash
python adt-client.py ... objects '$TMP'
python adt-client.py ... objects ZPACKAGE --max 500
```

### `packages` — List sub-packages of a parent package
```bash
python adt-client.py ... packages '$TMP'
python adt-client.py ... packages ZROOT_PACKAGE
```

### `packages-by-responsible` — List packages owned by a user
```bash
python adt-client.py ... packages-by-responsible LEOS4
python adt-client.py ... packages-by-responsible LEOS4 --pattern "Z*" --max 500
```
Fetches each matching package's properties and filters by `adtcore:responsible`.

### `source` — Read source code of an ABAP object
```bash
python adt-client.py ... source ZCDS_VIEW --type PROG/P
python adt-client.py ... source ZCL_MY_CLASS --type CLAS/OC
```
Supported types: `PROG/P` `CLAS/OC` `INTF/OI` `FUGR/FF`

### `transports` — List open transport requests
```bash
python adt-client.py ... transports
python adt-client.py ... transports --owner DEVUSER
```

## Output

All commands return **JSON** — easy to parse, filter with `jq`, or pass to next steps.

```json
[
  { "uri": "/sap/bc/adt/programs/programs/zcds_view", "type": "PROG/P",
    "name": "ZCDS_VIEW", "package": "$TMP", "description": "Find CDS Views by Table Name" }
]
```

## Usage in Workflow

When a user asks to browse, search, or inspect the SAP repository and `adt-mcp-server` tools don't cover it:

1. Get connection details from the project's `.claude/settings.json` or ask the user
2. Run the appropriate command via the venv Python interpreter
3. Parse the JSON output and present results

## Covered Gaps

| Capability | MCP | This skill |
|------------|-----|------------|
| Search objects by name/type | ❌ | ✅ `search` |
| Search by package | ❌ | ✅ `search --package` |
| List all objects in a package | ❌ | ✅ `objects` |
| Browse sub-packages | ❌ | ✅ `packages` |
| List packages by responsible user | ❌ | ✅ `packages-by-responsible` |
| Read source code | ❌ | ✅ `source` |
| List transport requests | ❌ | ✅ `transports` |
