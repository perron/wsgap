# AGENTS.md

Notes for coding agents working on or with wsgap.

## Using wsgap on a project

1. `pip install .` from this repo (Python 3.9+, no dependencies).
2. `wsgap scan <project> --exclude 'tests/*' --format json` gives one result per Workspace REST call with `status`, `tools`, `note` and `mcp_endpoint`.
3. Work through `none` results first: they have no MCP tool and need a different plan.
4. Before replacing a call, read the tool's reference page (linked from https://developers.google.com/workspace/guides/mcp-server-tools). A `direct` status means the same job, not identical parameters.

## Working on wsgap

- Layout: `src/wsgap/catalog.py` (parse Google's tool list), `catalog.json` (bundled snapshot), `mapping.py` (REST method to MCP tool, hand written), `urls.py` (raw REST URL parsing), `scanner.py` (finding calls), `report.py` and `cli.py`.
- Run `pytest` after every change. Tests check that each mapped tool exists in the catalog and that README example output matches the tool.
- If you change output, regenerate the README blocks marked `<!-- demo-output -->` and `<!-- lookup-output -->` from real runs.
- Every mapping change needs a link to the Google reference page that supports it, in the PR description.
- Keep it stdlib only.
