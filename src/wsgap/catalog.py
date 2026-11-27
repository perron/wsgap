"""Load and build the Workspace MCP tool catalog.

The catalog is parsed from Google's public reference page
"All Google Workspace MCP server tools" (Markdown version):
https://developers.google.com/workspace/guides/mcp-server-tools.md.txt
"""

from __future__ import annotations

import json
import re
import urllib.request
from importlib import resources
from typing import Dict, List, Optional

SOURCE_URL = "https://developers.google.com/workspace/guides/mcp-server-tools.md.txt"

# Section heading in the docs page -> our API key.
SECTION_TO_API = {
    "Gmail": "gmail",
    "Drive": "drive",
    "Docs": "docs",
    "Sheets": "sheets",
    "Slides": "slides",
    "Calendar": "calendar",
    "Chat": "chat",
    "Tasks": "tasks",
    "People API": "people",
}

_HEADING = re.compile(r"^##\s+(.+?)\s+toolsets?\s*$")
_ROW = re.compile(r"^\|\s*\[?`(?P<name>[a-z_]+)`\]?(?:\((?P<url>[^)]*)\))?\s*\|(?P<desc>.*?)\|\s*(?P<access>Read-only|Write)\s*\|(?P<sets>.*?)\|\s*$")
_ENDPOINT = re.compile(r"Primary endpoint:\s*`(https://[^`]+?)/mcp/v1`")


def parse_docs_markdown(text: str) -> Dict:
    """Parse the docs page Markdown into a catalog dict.

    Returns {"servers": {api: {"endpoint": url, "self_mode": bool,
    "tools": {name: {"access": ..., "toolsets": [...], "description": ...}}}}}.
    """
    servers: Dict[str, Dict] = {}
    current: Optional[str] = None
    for line in text.splitlines():
        m = _HEADING.match(line.strip())
        if m:
            current = SECTION_TO_API.get(m.group(1).strip())
            if current:
                servers[current] = {"endpoint": None, "self_mode": False, "tools": {}}
            continue
        if not current:
            continue
        e = _ENDPOINT.search(line)
        if e:
            servers[current]["endpoint"] = e.group(1) + "/mcp/v1"
            continue
        r = _ROW.match(line.strip())
        if r:
            sets = re.findall(r"/mcp/v1(?:self)?", r.group("sets"))
            if "/mcp/v1self" in sets:
                servers[current]["self_mode"] = True
            servers[current]["tools"][r.group("name")] = {
                "access": r.group("access"),
                "toolsets": sets,
                "description": r.group("desc").strip(),
                "reference": _html_url(r.group("url")),
            }
    servers = {k: v for k, v in servers.items() if v["tools"]}
    if not servers:
        raise ValueError("no MCP tool tables found in the input; is this the right page?")
    return {"source": SOURCE_URL, "servers": servers}


def _html_url(url: Optional[str]) -> Optional[str]:
    """Tool reference link as a normal web page.

    The page links to "<tool>.md.txt" copies, but some of those return 404
    and others are older than the web page, so we keep the web page URL.
    """
    if not url:
        return None
    return url[: -len(".md.txt")] if url.endswith(".md.txt") else url


def fetch_docs_markdown(url: str = SOURCE_URL, timeout: float = 30.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "wsgap"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def load_catalog(path: Optional[str] = None) -> Dict:
    """Load a catalog JSON file, or the snapshot bundled with the package."""
    if path:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    data = resources.files("wsgap").joinpath("catalog.json").read_text(encoding="utf-8")
    return json.loads(data)


def tool_info(catalog: Dict, api: str, tool: str) -> Optional[Dict]:
    return catalog.get("servers", {}).get(api, {}).get("tools", {}).get(tool)


def in_self_mode(catalog: Dict, api: str, tool: str) -> bool:
    """True if the tool can be called from the /mcp/v1self endpoint.

    Servers with no self-mode endpoint at all (People API) don't use form
    elicitation, so their tools count as callable.
    """
    server = catalog.get("servers", {}).get(api)
    info = tool_info(catalog, api, tool)
    if not server or not info:
        return False
    if not server.get("self_mode"):
        return True
    return "/mcp/v1self" in info["toolsets"]


def all_tools(catalog: Dict) -> List[tuple]:
    out = []
    for api, server in sorted(catalog.get("servers", {}).items()):
        for name in sorted(server["tools"]):
            out.append((api, name))
    return out
