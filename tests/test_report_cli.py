import json
import os
import re
import subprocess
import sys
from pathlib import Path

from wsgap import catalog as cat
from wsgap import report, scanner
from wsgap.cli import main

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "examples" / "demo-agent"
FIXTURE = Path(__file__).parent / "fixture_mcp-server-tools_2026-11-27.md"


def run(*args):
    p = subprocess.run([sys.executable, "-m", "wsgap", *args], capture_output=True, text=True, cwd=ROOT)
    return p.returncode, p.stdout, p.stderr


def test_self_mode_turns_v1_only_into_none():
    c = cat.load_catalog()
    assert report.resolve_method("gmail", "users.messages.send", c)[0] == "direct"
    status, refs, note = report.resolve_method("gmail", "users.messages.send", c, self_mode=True)
    assert status == "none" and "self-mode" in note
    assert report.resolve_method("gmail", "users.drafts.create", c, self_mode=True)[0] == "direct"


def test_missing_tool_in_custom_catalog_becomes_none():
    c = cat.load_catalog()
    del c["servers"]["gmail"]["tools"]["get_message"]
    status, refs, note = report.resolve_method("gmail", "users.messages.get", c)
    assert status == "none" and "not in this catalog" in note


def test_unclear_url_and_fail_levels():
    from wsgap.cli import should_fail
    c = cat.load_catalog()
    src = 'U = "https://gmail.googleapis.com/gmail/v1/users/me/messages/abc"\n'
    res = report.resolve(scanner.scan_text(src, "a.py"), c)
    assert len(res) == 1 and res[0].status == "unclear" and res[0].worst == "none"
    assert should_fail(res, "none")
    assert not should_fail(res, "never")
    direct = report.resolve(scanner.scan_text('s.users().threads().get(userId="me", id=i)\n', "b.py"), c)
    assert direct[0].status == "direct"
    assert not should_fail(direct, "none") and not should_fail(direct, "partial") and should_fail(direct, "any")


def test_demo_scan_exit_codes():
    code, out, _ = run("scan", "examples/demo-agent")
    assert code == 1
    code, out, _ = run("scan", "examples/demo-agent", "--fail-on", "never")
    assert code == 0
    code, out, err = run("scan", "no/such/dir")
    assert code == 2 and "no such file" in err


def test_demo_json_summary():
    code, out, _ = run("scan", "examples/demo-agent", "--format", "json", "--fail-on", "never")
    data = json.loads(out)
    s = data["summary"]
    assert (s["calls"], s["direct"], s["partial"], s["none"], s["unclear"]) == (17, 10, 2, 5, 0)
    assert data["files_scanned"] == 4
    send = [r for r in data["results"] if r["method"] == "users.drafts.send"][0]
    assert send["tools"][0]["name"] == "send_message" and send["tools"][0]["v1_only"] is True
    assert send["mcp_endpoint"] == "https://gmailmcp.googleapis.com/mcp/v1"


def test_lookup_and_tools_commands():
    code, out, _ = run("lookup", "gmail", "users.drafts.send")
    assert code == 0 and out.startswith("DIRECT  gmail users.drafts.send  ->  send_message [/mcp/v1 only]")
    code, out, _ = run("lookup", "drive", "drive.permissions.create")
    assert code == 0 and out.startswith("NONE  drive permissions.create")
    code, out, err = run("lookup", "gmail", "users.bogus")
    assert code == 2
    code, out, _ = run("tools", "gmail")
    assert "gmail  https://gmailmcp.googleapis.com/mcp/v1  (30 tools, 25 on /mcp/v1self)" in out
    assert re.search(r"send_message\s+write, /mcp/v1 only", out)
    code, out, _ = run("tools", "people")
    assert "(3 tools, no /mcp/v1self endpoint)" in out


def test_refresh_from_file(tmp_path):
    out_file = tmp_path / "cat.json"
    code, out, _ = run("refresh", "--from-file", str(FIXTURE), "--out", str(out_file))
    assert code == 0
    assert "9 servers, 90 tools" in out
    assert "Changes vs bundled snapshot: none" in out
    assert "Mapped tools missing" not in out
    code, out, _ = run("scan", "--catalog", str(out_file), "examples/demo-agent", "--fail-on", "never")
    assert code == 0 and "17 Workspace REST call(s)" in out


def test_refresh_reports_removed_tool(tmp_path):
    text = FIXTURE.read_text(encoding="utf-8")
    text = "\n".join(l for l in text.splitlines() if "tools_list/send_message" not in l or "/gmail/" not in l)
    src = tmp_path / "page.md"
    src.write_text(text)
    out_file = tmp_path / "cat.json"
    code, out, _ = run("refresh", "--from-file", str(src), "--out", str(out_file))
    assert code == 0
    assert "- gmail:send_message" in out
    assert "Mapped tools missing from the new catalog: gmail:send_message" in out


def _readme_block(marker):
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"<!-- " + marker + r" -->\n```[a-z]*\n(.*?)```", text, re.S)
    assert m, marker
    return m.group(1)


def test_readme_demo_output_matches():
    block = _readme_block("demo-output")
    lines = block.splitlines()
    assert lines[0].startswith("$ wsgap scan examples/demo-agent")
    code, out, _ = run("scan", "examples/demo-agent")
    assert "\n".join(lines[1:]).strip() == out.strip()


def test_readme_lookup_output_matches():
    block = _readme_block("lookup-output")
    lines = block.splitlines()
    cmd = lines[0][2:].split()
    assert cmd[0] == "wsgap"
    code, out, _ = run(*cmd[1:])
    assert "\n".join(lines[1:]).strip() == out.strip()
