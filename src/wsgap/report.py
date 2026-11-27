"""Resolve findings against the mapping and catalog, and format output."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import catalog as cat
from . import mapping
from .scanner import Finding

# "unclear": a URL whose HTTP verb wasn't found, and the possible methods differ.
ORDER = {"none": 0, "unclear": 1, "partial": 2, "direct": 3}


@dataclass
class ToolRef:
    api: str
    name: str
    exists: bool
    v1_only: bool
    usable: bool  # exists, and callable in the chosen mode


@dataclass
class Result:
    finding: Finding
    status: str
    tools: List[ToolRef] = field(default_factory=list)
    note: str = ""
    worst: str = ""  # worst status among candidate methods (same as status unless unclear)


def _ref(catalog: Dict, api: str, tool: str, self_mode: bool) -> ToolRef:
    if ":" in tool:
        api, tool = tool.split(":", 1)
    info = cat.tool_info(catalog, api, tool)
    exists = info is not None
    selfok = cat.in_self_mode(catalog, api, tool) if exists else False
    server = catalog.get("servers", {}).get(api, {})
    v1_only = exists and server.get("self_mode", False) and not selfok
    usable = exists and (selfok or not self_mode)
    return ToolRef(api, tool, exists, v1_only, usable)


def resolve_method(api: str, method: str, catalog: Dict, self_mode: bool = False):
    entry = mapping.lookup(api, method)
    if entry is None:
        return None
    status, tools, note = entry
    refs = [_ref(catalog, api, t, self_mode) for t in tools]
    if status != "none":
        usable = [r for r in refs if r.usable]
        if not usable:
            missing = [r.name for r in refs if not r.exists]
            if missing:
                note = (note + " " if note else "") + "Mapped tool not in this catalog: " + ", ".join(missing) + "."
            else:
                note = (note + " " if note else "") + "Only on /mcp/v1, and --self-mode is set."
            status = "none"
        elif len(usable) < len(refs) and status == "direct" and self_mode:
            # The main tool is gone in self mode but a helper remains.
            if not refs[0].usable:
                status = "partial"
    return status, refs, note


def resolve(findings: List[Finding], catalog: Dict, self_mode: bool = False) -> List[Result]:
    out = []
    for f in findings:
        r = resolve_method(f.api, f.method, catalog, self_mode)
        if r is None:
            continue
        status, refs, note = r
        worst = status
        if f.kind == "url" and len(f.candidates) > 1:
            parts = [f"{f.method}: {status}"]
            statuses = {status}
            seen = {(t.api, t.name) for t in refs}
            for c in f.candidates[1:]:
                rc = resolve_method(f.api, c, catalog, self_mode)
                if not rc:
                    continue
                statuses.add(rc[0])
                parts.append(f"{c}: {rc[0]}")
                if ORDER[rc[0]] < ORDER[worst]:
                    worst = rc[0]
                for t in rc[1]:
                    if (t.api, t.name) not in seen:
                        refs.append(t)
                        seen.add((t.api, t.name))
            if len(statuses) > 1:
                status = "unclear"
                note = "HTTP verb not found near the URL. " + "; ".join(parts) + "."
        out.append(Result(f, status, refs, note, worst))
    return out


def _tool_label(t: ToolRef, default_api: str) -> str:
    name = t.name if t.api == default_api else f"{t.api}:{t.name}"
    flags = []
    if not t.exists:
        flags.append("not in catalog")
    if t.v1_only:
        flags.append("/mcp/v1 only")
    return name + (f" [{', '.join(flags)}]" if flags else "")


def _method_label(r: Result) -> str:
    f = r.finding
    if r.status == "unclear":
        return " | ".join(f.candidates)
    return f.method


def summary(results: List[Result]) -> Dict:
    counts = {"direct": 0, "partial": 0, "unclear": 0, "none": 0}
    files = set()
    for r in results:
        counts[r.status] += 1
        files.add(r.finding.path)
    return {"calls": len(results), "files": len(files), **counts}


def format_text(results: List[Result], catalog: Dict, nfiles: int, base: Optional[str] = None) -> str:
    lines = []
    for r in sorted(results, key=lambda r: (ORDER[r.status], r.finding.path, r.finding.line)):
        f = r.finding
        path = os.path.relpath(f.path, base) if base else f.path
        tools = ", ".join(_tool_label(t, f.api) for t in r.tools) or "-"
        lines.append(f"{r.status.upper():8} {path}:{f.line}  {f.api} {_method_label(r)}  ->  {tools}")
        if r.note:
            lines.append(f"{'':9}{r.note}")
    s = summary(results)
    if lines:
        lines.append("")
    lines.append(
        f"{s['calls']} Workspace REST call(s) in {s['files']} of {nfiles} scanned file(s): "
        f"{s['direct']} direct, {s['partial']} partial, {s['none']} none"
        + (f", {s['unclear']} unclear." if s["unclear"] else ".")
    )
    lines.append(f"Catalog: {catalog.get('source', '?')} (fetched {catalog.get('fetched', '?')}).")
    return "\n".join(lines)


def format_json(results: List[Result], catalog: Dict, nfiles: int) -> str:
    items = []
    for r in results:
        f = r.finding
        items.append({
            "path": f.path, "line": f.line, "api": f.api, "method": f.method,
            "kind": f.kind, "status": r.status, "worst_status": r.worst or r.status, "note": r.note,
            "candidates": f.candidates or [f.method], "http_verb": f.http_verb,
            "code": f.text,
            "mcp_endpoint": catalog.get("servers", {}).get(f.api, {}).get("endpoint"),
            "tools": [{"api": t.api, "name": t.name, "in_catalog": t.exists,
                       "v1_only": t.v1_only, "usable": t.usable,
                       "reference": (cat.tool_info(catalog, t.api, t.name) or {}).get("reference")} for t in r.tools],
        })
    return json.dumps({
        "catalog": {"source": catalog.get("source"), "fetched": catalog.get("fetched")},
        "files_scanned": nfiles, "summary": summary(results), "results": items,
    }, indent=2)


def format_markdown(results: List[Result], catalog: Dict, nfiles: int, base: Optional[str] = None) -> str:
    out = ["| Status | Location | REST method | MCP tool | Note |", "|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: (ORDER[r.status], r.finding.path, r.finding.line)):
        f = r.finding
        path = os.path.relpath(f.path, base) if base else f.path
        tools = ", ".join(_tool_label(t, f.api) for t in r.tools) or "-"
        note = r.note.replace("|", "\\|")
        method = _method_label(r).replace("|", "\\|")
        out.append(f"| {r.status} | `{path}:{f.line}` | `{f.api} {method}` | {tools} | {note} |")
    s = summary(results)
    out.append("")
    out.append(f"{s['calls']} call(s) in {s['files']} of {nfiles} file(s): {s['direct']} direct, "
               f"{s['partial']} partial, {s['none']} none, {s['unclear']} unclear. Catalog fetched {catalog.get('fetched', '?')}.")
    return "\n".join(out)
