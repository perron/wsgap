"""Command line interface for wsgap."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from typing import List, Optional

from . import __version__
from . import catalog as cat
from . import mapping, report, scanner

FAIL_LEVELS = ("none", "partial", "any", "never")


def _load(args) -> dict:
    return cat.load_catalog(getattr(args, "catalog", None))


def cmd_scan(args) -> int:
    catalog = _load(args)
    for p in args.paths:
        if not os.path.exists(p):
            print(f"wsgap: no such file or directory: {p}", file=sys.stderr)
            return 2
    findings, nfiles = scanner.scan_paths(args.paths, exclude=args.exclude or ())
    if nfiles == 0:
        print("wsgap: no files to scan (check the path and --exclude)", file=sys.stderr)
        return 2
    results = report.resolve(findings, catalog, self_mode=args.self_mode)
    base = args.paths[0] if len(args.paths) == 1 and os.path.isdir(args.paths[0]) else None
    if args.format == "json":
        print(report.format_json(results, catalog, nfiles))
    elif args.format == "md":
        print(report.format_markdown(results, catalog, nfiles, base))
    else:
        print(report.format_text(results, catalog, nfiles, base))
    return 1 if should_fail(results, args.fail_on) else 0


def should_fail(results, level: str) -> bool:
    """none: any call with no MCP tool (an unclear URL counts if one reading has none).
    partial: any call that isn't direct. any: any call at all. never: never."""
    if level == "never" or not results:
        return False
    if level == "any":
        return True
    for r in results:
        worst = r.worst or r.status
        if worst == "none":
            return True
        if level == "partial" and r.status != "direct":
            return True
    return False


def cmd_lookup(args) -> int:
    catalog = _load(args)
    api = args.api.lower()
    if api not in mapping.MAPPING:
        print(f"wsgap: unknown API {args.api!r}; use one of: {', '.join(mapping.MAPPING)}", file=sys.stderr)
        return 2
    method = args.method
    # Accept "gmail.users.messages.send", but keep "tasks.insert" and "people.get" as is.
    if mapping.lookup(api, method) is None and method.startswith(api + "."):
        method = method[len(api) + 1:]
    r = report.resolve_method(api, method, catalog, self_mode=args.self_mode)
    if r is None:
        print(f"wsgap: no mapping for {api} {method}", file=sys.stderr)
        return 2
    status, refs, note = r
    tools = ", ".join(report._tool_label(t, api) for t in refs) or "-"
    print(f"{status.upper()}  {api} {method}  ->  {tools}")
    if note:
        print(f"  {note}")
    endpoint = catalog.get("servers", {}).get(api, {}).get("endpoint")
    if endpoint:
        print(f"  MCP server: {endpoint}")
    for t in refs:
        info = cat.tool_info(catalog, t.api, t.name)
        if info and info.get("reference"):
            print(f"  {t.name}: {info['reference']}")
    return 0


def cmd_tools(args) -> int:
    catalog = _load(args)
    servers = catalog.get("servers", {})
    apis = [args.api.lower()] if args.api else sorted(servers)
    for api in apis:
        server = servers.get(api)
        if not server:
            print(f"wsgap: API {api!r} not in catalog", file=sys.stderr)
            return 2
        n_self = sum(1 for t in server["tools"] if cat.in_self_mode(catalog, api, t)) if server.get("self_mode") else None
        extra = f", {n_self} on /mcp/v1self" if n_self is not None else ", no /mcp/v1self endpoint"
        print(f"{api}  {server.get('endpoint')}  ({len(server['tools'])} tools{extra})")
        for name in sorted(server["tools"]):
            info = server["tools"][name]
            flags = [info["access"].lower()]
            if server.get("self_mode") and "/mcp/v1self" not in info["toolsets"]:
                flags.append("/mcp/v1 only")
            print(f"  {name:36} {', '.join(flags)}")
    print(f"Catalog: {catalog.get('source')} (fetched {catalog.get('fetched', '?')}).")
    return 0


def cmd_refresh(args) -> int:
    if args.from_file:
        with open(args.from_file, encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = cat.fetch_docs_markdown()
    new = cat.parse_docs_markdown(text)
    new["fetched"] = datetime.date.today().isoformat()
    old = cat.load_catalog(None)
    # Report changes against the bundled snapshot and mapped tools that disappeared.
    changes = []
    for api in sorted(set(old["servers"]) | set(new["servers"])):
        o = set(old["servers"].get(api, {}).get("tools", {}))
        n = set(new["servers"].get(api, {}).get("tools", {}))
        for t in sorted(n - o):
            changes.append(f"+ {api}:{t}")
        for t in sorted(o - n):
            changes.append(f"- {api}:{t}")
    gone = []
    for api, table in mapping.MAPPING.items():
        for _, (status, tools, _) in table.items():
            for t in tools:
                a, name = (t.split(":", 1) if ":" in t else (api, t))
                if cat.tool_info(new, a, name) is None:
                    gone.append(f"{a}:{name}")
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(new, fh, indent=1, sort_keys=True)
        fh.write("\n")
    total = sum(len(s["tools"]) for s in new["servers"].values())
    print(f"Wrote {args.out}: {len(new['servers'])} servers, {total} tools.")
    print("Changes vs bundled snapshot: " + (", ".join(changes) if changes else "none"))
    if gone:
        print("Mapped tools missing from the new catalog: " + ", ".join(sorted(set(gone))))
    print(f"Use it with: wsgap scan --catalog {args.out} PATH")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wsgap",
        description="Find Google Workspace REST calls in code and show which Workspace MCP tool replaces each one.",
    )
    p.add_argument("--version", action="version", version=f"wsgap {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--catalog", help="catalog JSON from 'wsgap refresh' (default: bundled snapshot)")
        sp.add_argument("--self-mode", action="store_true",
                        help="your MCP client has no form elicitation, so only /mcp/v1self tools count")

    s = sub.add_parser("scan", help="scan files or folders for Workspace REST calls")
    s.add_argument("paths", nargs="+")
    s.add_argument("--format", choices=("text", "json", "md"), default="text")
    s.add_argument("--exclude", action="append", metavar="GLOB",
                   help="skip files whose path (relative to the scanned folder) matches, e.g. 'tests/*'. Repeatable.")
    s.add_argument("--fail-on", choices=FAIL_LEVELS, default="none",
                   help="exit 1 when a call has this status or worse: none (default), partial, any call, never")
    common(s)
    s.set_defaults(func=cmd_scan)

    l = sub.add_parser("lookup", help="show the MCP tool for one REST method, e.g. 'lookup gmail users.messages.send'")
    l.add_argument("api")
    l.add_argument("method")
    common(l)
    l.set_defaults(func=cmd_lookup)

    t = sub.add_parser("tools", help="list MCP tools in the catalog")
    t.add_argument("api", nargs="?")
    t.add_argument("--catalog")
    t.set_defaults(func=cmd_tools)

    r = sub.add_parser("refresh", help="rebuild the catalog from Google's docs page")
    r.add_argument("--out", default="wsgap-catalog.json")
    r.add_argument("--from-file", help="parse a saved copy of the docs Markdown instead of downloading it")
    r.set_defaults(func=cmd_refresh)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError) as e:
        print(f"wsgap: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
