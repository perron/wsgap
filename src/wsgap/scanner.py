"""Find Workspace REST calls in source files."""

from __future__ import annotations

import bisect
import fnmatch
import os
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import mapping, urls

CODE_EXTS = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".mts", ".cts",
    ".go", ".java", ".kt", ".kts", ".sh", ".bash", ".zsh", ".ps1",
}
# Config files: only REST URLs are looked for, not client library calls.
CONFIG_EXTS = {".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".env"}
CONFIG_NAMES = {"Makefile", "makefile", "GNUmakefile", "Dockerfile", "Justfile", "justfile"}
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", ".tox", "dist", "build", ".next", ".mypy_cache", ".pytest_cache",
    "site-packages", "vendor",
}
MAX_BYTES = 2_000_000
SHELL_EXTS = {".sh", ".bash", ".zsh", ".ps1"}

# Client library names -> our API key. Anything else bound with build()/NewService
# is recorded as "other" so its calls are ignored.
LIB_NAMES = {
    "gmail": "gmail", "drive": "drive", "calendar": "calendar", "sheets": "sheets",
    "docs": "docs", "slides": "slides", "chat": "chat", "hangoutschat": "chat",
    "tasks": "tasks", "people": "people", "peopleservice": "people",
}
# Words in a receiver name that point at one API, for example gmail_service or driveClient.
HINTS = {
    "gmail": ("gmail", "mail"), "drive": ("drive",), "calendar": ("calendar",),
    "sheets": ("sheets", "sheet"), "docs": ("docs",), "slides": ("slides",),
    "chat": ("chat",), "tasks": ("tasks",), "people": ("people", "contacts"),
}
# Two-segment resources that no other Google API uses at the top level.
UNIQUE_TOP = {
    "drive": {"files", "permissions", "revisions", "drives", "accessproposals"},
    "calendar": {"events", "calendarList", "acl", "freebusy", "calendars"},
    "sheets": {"spreadsheets"}, "docs": {"documents"}, "slides": {"presentations"},
    "chat": {"spaces"}, "tasks": {"tasklists", "tasks"}, "people": {"contactGroups", "otherContacts", "people"},
    "gmail": set(),
}
LIB_MARKERS = (
    "googleapiclient", "googleapis", "google.golang.org/api", "com.google.api.services",
    "discovery.build", "aiogoogle", "google-api-python-client", "@googleapis/",
)

_BIND_PATTERNS = [
    # Python: svc = build("gmail", "v1", ...)   self.svc = discovery.build(serviceName="drive", ...)
    re.compile(r"([A-Za-z_]\w*)\s*(?::\s*[\w.\[\]]+\s*)?=\s*(?:await\s+)?(?:[\w.]*\.)?build\(\s*(?:serviceName\s*=\s*)?['\"](\w+)['\"]"),
    # Node: const gmail = google.gmail({version: "v1"})   drive = google.drive("v3")
    re.compile(r"([A-Za-z_$][\w$]*)\s*(?::\s*[\w.<>\[\]]+\s*)?=\s*(?:await\s+)?google\s*\.\s*(\w+)\s*\("),
    # Node: new gmail_v1.Gmail(...)
    re.compile(r"([A-Za-z_$][\w$]*)\s*(?::\s*[\w.<>]+\s*)?=\s*new\s+(\w+?)_v\w+\s*\."),
    # Go: srv, err := gmail.NewService(ctx, ...)
    re.compile(r"([A-Za-z_]\w*)\s*,\s*\w+\s*:?=\s*(\w+)\.NewService\("),
    # Java/Kotlin: Gmail service = new Gmail.Builder(...)
    re.compile(r"([A-Za-z_]\w*)\s*=\s*(?:new\s+)?(\w+)\.Builder\("),
    # Go parameter or field: srv *drive.Service
    re.compile(r"\b([A-Za-z_]\w*)\s+\*(\w+)\.Service\b"),
]

_CHAIN = re.compile(
    r"(?<![\w$.?])(?P<recv>[A-Za-z_$][\w$]*)(?P<chain>(?:\s*(?:\(\s*\))?\s*\??\.\s*[A-Za-z_]\w*){2,7})\s*\("
)
_SEG = re.compile(r"(\(\s*\))?\s*\??\.\s*([A-Za-z_]\w*)")
_COMMENT_LINE = re.compile(r"^\s*(?:#(?!!)|//|/\*|\*|--\s|REM\s)")


@dataclass
class Finding:
    path: str
    line: int
    api: str
    method: str
    kind: str  # "client" or "url"
    text: str
    candidates: List[str] = field(default_factory=list)
    http_verb: Optional[str] = None


def _excluded(rel: str, patterns: Sequence[str]) -> bool:
    rel = os.path.normpath(rel).replace(os.sep, "/")
    for pat in patterns:
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, "*/" + pat):
            return True
    return False


def iter_files(paths: Iterable[str], exts=None, exclude: Sequence[str] = ()) -> Iterable[str]:
    """Yield source files under paths. Files named directly are always scanned.

    exclude: glob patterns matched against the path relative to each scanned
    folder, for example "tests/*" or "*_test.go".
    """
    exts = exts or (CODE_EXTS | CONFIG_EXTS)
    for p in paths:
        if os.path.isfile(p):
            if not (exclude and _excluded(p, exclude)):
                yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                if os.path.splitext(name)[1].lower() not in exts and name not in CONFIG_NAMES:
                    continue
                full = os.path.join(root, name)
                if exclude and _excluded(os.path.relpath(full, p), exclude):
                    continue
                yield full


_REQUIRE = re.compile(r"([A-Za-z_$][\w$]*)\s*=\s*require\(\s*['\"]([^'\"]+)['\"]\s*\)")


def find_bindings(text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    # const drive = require("./my-drive") is not a Google client.
    for m in _REQUIRE.finditer(text):
        if "googleapis" not in m.group(2):
            out[m.group(1)] = "other"
    for pat in _BIND_PATTERNS:
        for m in pat.finditer(text):
            var, lib = m.group(1), m.group(2).lower()
            out[var] = LIB_NAMES.get(lib, "other")
    return out


def _line_of(text: str, offset: int, starts: List[int]) -> int:
    return bisect.bisect_right(starts, offset)


def _match_key(segs: List[str], key: str) -> bool:
    kparts = key.split(".")
    if len(kparts) != len(segs):
        return False
    for k, s in zip(kparts, segs):
        if k != "*" and k.lower() != s.lower():
            return False
    return True


_RESOURCE_NAMES: Dict[str, set] = {}


def _resource_names(api: str) -> set:
    """Lower-cased names used as resources (not methods) in this API's keys."""
    if api not in _RESOURCE_NAMES:
        names = set()
        for key in mapping.MAPPING[api]:
            for part in key.split(".")[:-1]:
                if part != "*":
                    names.add(part.lower())
        _RESOURCE_NAMES[api] = names
    return _RESOURCE_NAMES[api]


def _canon(api: str, segs: List[str]) -> Optional[str]:
    """Map case-insensitive segments (Go uses Users.Messages.Send) to a mapping key."""
    best = None
    best_score = -1
    for key in mapping.MAPPING[api]:
        if key.endswith(".*") and segs[-1].lower() in _resource_names(api):
            continue  # "spaces().messages()" is a resource, not a method on spaces
        if _match_key(segs, key):
            score = sum(1 for k in key.split(".") if k != "*")
            if score > best_score:
                best, best_score = key, score
    if best is None:
        return None
    # Rebuild with the key's spelling where fixed, the source's where wildcard.
    out = []
    for k, s in zip(best.split("."), segs):
        out.append(s if k == "*" else k)
    return ".".join(out)


def _try_window(names, called, start, end, bindings, has_marker):
    segs_try = names[start:end]
    receiver = names[start - 1]
    if called[start - 1]:
        return None  # nested under another resource, e.g. projects().databases().documents()
    bound = bindings.get(receiver)
    for api in mapping.MAPPING:
        key = _canon(api, segs_try)
        if not key:
            continue
        if bound and bound != api:
            continue
        if len(segs_try) >= 3 or bound == api:
            return api, key
        # Two segments, e.g. files.list: needs more evidence than the path itself.
        resource = segs_try[0]
        py_style = called[start]
        hinted = any(h in receiver.lower() for h in HINTS[api])
        unique = resource.lower() in {r.lower() for r in UNIQUE_TOP.get(api, set())}
        if has_marker and (hinted or unique):
            return api, key
        if hinted and py_style:
            return api, key
    return None


def scan_client_calls(text: str, path: str, starts: List[int], lines: List[str]) -> List[Finding]:
    bindings = find_bindings(text)
    has_marker = any(m in text for m in LIB_MARKERS)
    found: List[Finding] = []
    for m in _CHAIN.finditer(text):
        recv = m.group("recv")
        # Each _SEG match: optional "()" that belongs to the previous name, then ".name".
        prev_called = []
        names = [recv]
        for sm in _SEG.finditer(m.group("chain")):
            prev_called.append(bool(sm.group(1)))
            names.append(sm.group(2))
        called = prev_called + [False]  # called[i]: names[i] followed by "()"
        # Candidate ends: the last name (followed by "(") or any name followed by "()",
        # so trailing calls such as .execute() or .Do() are skipped. Longest first.
        ends = [len(names)] + [i + 1 for i in reversed(range(len(names) - 1)) if called[i]]
        hit = None
        for end in ends:
            for start in range(1, end - 1):
                hit = _try_window(names, called, start, end, bindings, has_marker)
                if hit:
                    break
            if hit:
                break
        if not hit:
            continue
        ln = _line_of(text, m.start(), starts)
        if _COMMENT_LINE.match(lines[ln - 1]):
            continue
        found.append(Finding(path, ln, hit[0], hit[1], "client", lines[ln - 1].strip()))
    return found


def scan_urls(text: str, path: str, starts: List[int], lines: List[str]) -> List[Finding]:
    found: List[Finding] = []
    for m in urls.URL_RE.finditer(text):
        split = urls.split_url(m.group("host"), m.group("path"))
        if not split:
            continue
        api, segs, upload = split
        parsed = urls.parse_path(api, segs)
        if not parsed:
            continue
        ln = _line_of(text, m.start(), starts)
        if _COMMENT_LINE.match(lines[ln - 1]):
            continue
        shell = os.path.splitext(path)[1].lower() in SHELL_EXTS or os.path.basename(path) in CONFIG_NAMES
        verb = urls.find_http_verb(lines, ln - 1, shell=shell)
        cands = urls.methods_for(api, parsed, verb, upload)
        mapped = [c for c in cands if mapping.lookup(api, c)]
        if not mapped:
            continue
        f = Finding(path, ln, api, mapped[0], "url", lines[ln - 1].strip(), candidates=mapped, http_verb=verb)
        found.append(f)
    return found


def scan_text(text: str, path: str) -> List[Finding]:
    lines = text.splitlines() or [""]
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    ext = os.path.splitext(path)[1].lower()
    is_config = ext in CONFIG_EXTS or os.path.basename(path) in CONFIG_NAMES
    findings = [] if is_config else scan_client_calls(text, path, starts, lines)
    findings += scan_urls(text, path, starts, lines)
    findings.sort(key=lambda f: (f.line, f.method))
    return findings


def scan_paths(paths: Iterable[str], exts=None, exclude: Sequence[str] = ()) -> Tuple[List[Finding], int]:
    findings: List[Finding] = []
    nfiles = 0
    for fp in iter_files(paths, exts, exclude):
        try:
            if os.path.getsize(fp) > MAX_BYTES:
                continue
            with open(fp, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        nfiles += 1
        findings.extend(scan_text(text, fp))
    return findings, nfiles
