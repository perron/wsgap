# wsgap

Find the Google Workspace REST calls in your code and see which Workspace MCP tool replaces each one, or that none does.

**Before:** you read nine MCP reference pages and grep your agent's code by hand to learn what still works after February 1, 2027.
**After:** `wsgap scan .` lists every Gmail, Drive, Calendar, Docs, Sheets, Slides, Chat, Tasks and People API call with its file and line, the MCP tool to use, and the calls that have no MCP tool at all.

## Why this exists

On November 24, 2026 Google made its Workspace MCP servers generally available and published the Workspace AI Tools Addendum. From February 1, 2027, an AI agent (or a tool driven by one) must reach Workspace data through those MCP servers or the Workspace CLI instead of calling the REST APIs directly. Google's technical enforcement of that rule begins on that date. A separate change, the new Standard and Scaled usage tiers, takes effect on April 1, 2027. Sources: [Google Workspace Updates post](https://workspaceupdates.googleblog.com/2026/11/mcp-servers-cli-standardized-usage-tiers-now-available.html), [usage tiers page](https://developers.google.com/workspace/guides/quota-usage-tiers).

The MCP servers don't cover the whole REST API. Gmail has no tool for attachment downloads or history sync. Drive has no sharing tool. Some tools only exist on the `/mcp/v1` endpoint, which needs an MCP client that supports form elicitation. So the first job of a migration is a list of what you call today and where each call lands. wsgap makes that list.

Inspired by the Tech Stackups article [Google Will Make AI Agents Use Its MCP Servers. The Gmail One Can't Send Email](https://techstackups.com/articles/google-workspace-ai-agents-mcp/) and its [Hacker News discussion](https://news.ycombinator.com/item?id=50653477). wsgap is built from Google's own reference pages, which differ from that article in places: the Gmail server does list `send_message`, `reply` and `forward` (on `/mcp/v1` only), and Drive's `update_file` takes a new `title` and `parentId`, so it can rename and move files.

## Install

Python 3.9 or newer. No dependencies.

```
git clone https://github.com/perron/wsgap
cd wsgap
python3 -m venv .venv && . .venv/bin/activate
pip install .
```

## Quick start

The repo has a small made-up agent in `examples/demo-agent` (demo data, not working code) with Python, TypeScript, Go and shell files. Scan it:

<!-- demo-output -->
```
$ wsgap scan examples/demo-agent
NONE     drive_report.ts:11  drive permissions.create  ->  -
         No sharing tool. request_access only asks the owner for access.
NONE     mail_triage.py:20  gmail users.messages.attachments.get  ->  -
         No tool downloads attachment data. get_message lists attachment ids and metadata only.
NONE     sync_history.sh:5  gmail users.history.list  ->  -
         No history or sync tool.
NONE     sync_history.sh:7  gmail users.messages.delete  ->  -
         Permanent delete has no tool. trash_message only moves to Trash.
NONE     tasks.go:21  tasks tasks.move  ->  -
PARTIAL  drive_report.ts:10  drive files.update  ->  update_file, upload_file_revision [/mcp/v1 only], trash_file
         update_file changes title, parentId (move), description, star and lock. New content goes through upload_file_revision (non-Google files only). Setting trashed: true is trash_file.
PARTIAL  mail_triage.py:9  gmail users.threads.list  ->  search_threads
         Drafts are always excluded (use list_drafts), pageSize is at most 50, and label: takes the label's display name, not its id.
PARTIAL  mail_triage.py:13  gmail users.threads.modify  ->  label_thread, unlabel_thread
         Adding and removing labels are separate calls.
PARTIAL  sync_history.sh:9  calendar events.list  ->  list_events
         Without an end time list_events covers 7 days from the start, and its schema has no singleEvents option. For keyword search on the primary calendar, Google points to search_events.
DIRECT   drive_report.ts:7  drive files.create  ->  create_file
DIRECT   drive_report.ts:15  sheets spreadsheets.values.append  ->  append_values
DIRECT   mail_triage.py:11  gmail users.threads.get  ->  get_thread
DIRECT   mail_triage.py:31  gmail users.drafts.create  ->  create_draft
DIRECT   mail_triage.py:32  gmail users.drafts.send  ->  send_message [/mcp/v1 only]
         Pass draftId to send_message.
DIRECT   mail_triage.py:37  calendar events.insert  ->  create_event
DIRECT   mail_triage.py:38  calendar calendarList.list  ->  list_calendars
DIRECT   tasks.go:17  tasks tasks.insert  ->  create_task

17 Workspace REST call(s) in 4 of 4 scanned file(s): 8 direct, 4 partial, 5 none.
Catalog: https://developers.google.com/workspace/guides/mcp-server-tools.md.txt (fetched 2026-11-27).
```

Each line is one call: status, file and line, the REST method, then the MCP tool or tools that replace it.

- `DIRECT`: one MCP tool does what the REST method does.
- `PARTIAL`: the closest tool covers part of it. The note says what is missing.
- `NONE`: no MCP tool does this. Plan another route, or ask Google for it.
- `UNCLEAR`: a raw URL where wsgap couldn't find the HTTP verb, and the possible methods land differently. The note lists each reading.

The flag `/mcp/v1 only` means the tool is not on the `/mcp/v1self` endpoint, so your MCP client needs form elicitation to call it.

The exit code is 1 when any call has no MCP tool, so you can use wsgap in CI (see below). It is 2 for usage errors, including when no files were scanned.

## Look up one method

<!-- lookup-output -->
```
$ wsgap lookup gmail users.drafts.send
DIRECT  gmail users.drafts.send  ->  send_message [/mcp/v1 only]
  Pass draftId to send_message.
  MCP server: https://gmailmcp.googleapis.com/mcp/v1
  send_message: https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/send_message
```

Method names are the ones the client libraries use: `users.messages.send` in Python (`service.users().messages().send()`), Node (`gmail.users.messages.send()`) and Go (`srv.Users.Messages.Send()`).

## Commands

```
wsgap scan PATH [PATH ...]      # scan files or folders
    --format text|json|md       # md prints a table for a PR or issue
    --exclude GLOB              # skip paths relative to the scanned folder, e.g. 'tests/*' (repeatable)
    --self-mode                 # count only tools on /mcp/v1self (your client has no form elicitation)
    --fail-on none|partial|any|never
                                # exit 1 on: a call with no tool (default), any call that isn't direct,
                                # any Workspace REST call at all, or never
    --catalog FILE              # use a catalog from 'wsgap refresh'
wsgap lookup API METHOD         # e.g. wsgap lookup drive files.update
wsgap tools [API]               # list the MCP tools in the catalog
wsgap refresh [--out FILE]      # rebuild the catalog from Google's docs page
```

### Use it in CI

Fail the build when new code adds a call that has no MCP tool:

```
wsgap scan src --exclude 'tests/*'
```

When you think the migration is done, check that no direct REST calls are left:

```
wsgap scan src --exclude 'tests/*' --fail-on any
```

### Keep the tool list current

wsgap ships a snapshot of Google's page [All Google Workspace MCP server tools](https://developers.google.com/workspace/guides/mcp-server-tools) taken on Nov 27 2026. Google says some tools are still rolling out, so the list will change. To rebuild it:

```
wsgap refresh --out wsgap-catalog.json
wsgap scan --catalog wsgap-catalog.json src
```

`refresh` downloads the Markdown version of that page. It prints tools added or removed since the bundled snapshot, and any tool the mapping uses that has disappeared. Add `--from-file page.md` to parse a saved copy instead.

## What it finds

- Client library calls in Python (google-api-python-client), JavaScript and TypeScript (googleapis), Go (google.golang.org/api) and Java or Kotlin, including chains split across lines and `?.` optional chaining.
- Raw REST URLs (`https://gmail.googleapis.com/gmail/v1/...`, `https://www.googleapis.com/drive/v3/...` and the rest) in those files, in shell scripts, and in config files (`.json`, `.yml`, `.yaml`, `.toml`, `.ini`, `.cfg`, `.env`, `Makefile`, `Dockerfile`). The HTTP verb comes from the same statement: `requests.post(`, `method: "PATCH"`, `curl -X DELETE`, or `curl` with `-d` (POST) or without (GET).
- Drive API v2 names and URLs (`files.insert`, `permissions.insert`, `/drive/v2/`) and the Python media helpers (`files().get_media()`, `files().export_media()`).
- Lines that start as a comment (`#`, `//`, `/*`, `*`) are skipped.

How it decides a call is a Google client call:

- Paths with three or more parts, such as `users().messages().send(`, always count.
- Two-part calls such as `files.list(` count when the receiver was created in the same file with `build("drive", ...)`, `google.drive(...)`, `drive.NewService(...)` or `new Drive.Builder(...)`, or is typed `*drive.Service` in Go.
- Otherwise a two-part call counts only when the file imports a Google client library and the receiver's name points at the API (`drive`, `driveService`) or the resource only exists in Workspace (`files`, `events`, `spreadsheets` and similar). A receiver named for the API in Python discovery style (`drive_service.files().list(`) also counts without the import.
- A receiver created for another API in the same file (`build("youtube", ...)`, `require("./my-drive")`) never counts.

## Limits

- The REST-to-MCP mapping was written by hand from Google's tool reference pages on Nov 27 2026. A `DIRECT` means the tool does the same job, not that every parameter matches. Read the tool's schema before you switch.
- wsgap reads code as text. It does not follow variables across files, so a URL built from pieces in different places, or a client passed through several layers with a generic name, can be missed. A call such as `build("drive", "v3").files().list()` on one line is also missed.
- Code inside docstrings and multi-line strings is reported like code. Comment lines are skipped.
- A three-part path such as `users().messages().send(` is reported even on an object that isn't a Google client.
- It only knows the nine generally available servers (Gmail, Drive, Docs, Sheets, Slides, Calendar, Chat, Tasks, People). Admin SDK, Classroom, Forms, Keep and Apps Script calls are ignored.
- It does not check OAuth clients, the "AI-powered agent" flag, quotas, or the addendum's data rules (for example the 30-day limit on stored embeddings). Those are in Google's [configuration guide](https://developers.google.com/workspace/guides/configure-mcp-servers).
- The gws and gwscli command line tools are not scanned.

## Related

- [jeffdrizzy/google-workspace-agent-skill](https://github.com/jeffdrizzy/google-workspace-agent-skill) is an agent skill for the same migration. Its check script looks for Workspace REST hostnames and an MCP config. wsgap goes one level deeper: each client library call and URL, mapped to a tool.

## Point your agent at it

This repo is small and has an `AGENTS.md`. If you run a coding agent, point it here and ask it to run `wsgap scan` on your project and draft the migration plan from the output. Or write your own version; the mapping in `src/wsgap/mapping.py` is the part worth reusing.

## How to help

- Found a call wsgap missed, or a false alarm? Open an issue with the smallest code snippet that shows it.
- Mapping wrong for a method? Each entry in `src/wsgap/mapping.py` is one line. Send a fix with a link to the tool reference page that backs it.
- Run `pip install -e '.[dev]' && pytest` before you open a pull request. The tests check that every tool named in the mapping exists in the catalog, and that this README's example output matches the real output.

## License

MIT. See `LICENSE`.
