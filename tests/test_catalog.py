import json
from pathlib import Path

from wsgap import catalog as cat
from wsgap import mapping

FIXTURE = Path(__file__).parent / "fixture_mcp-server-tools_2026-11-27.md"

# Tool counts from the summary table at the top of Google's page (Nov 27 2026).
DOC_COUNTS = {
    "gmail": (30, 25), "drive": (15, 12), "docs": (2, 2), "sheets": (9, 9),
    "slides": (4, 4), "calendar": (9, 8), "chat": (9, 8), "tasks": (9, 8),
    "people": (3, None),
}


def test_parse_fixture_matches_doc_summary_counts():
    c = cat.parse_docs_markdown(FIXTURE.read_text(encoding="utf-8"))
    assert set(c["servers"]) == set(DOC_COUNTS)
    for api, (n_v1, n_self) in DOC_COUNTS.items():
        tools = c["servers"][api]["tools"]
        assert len(tools) == n_v1, api
        if n_self is None:
            assert c["servers"][api]["self_mode"] is False
        else:
            assert sum("/mcp/v1self" in t["toolsets"] for t in tools.values()) == n_self, api


def test_bundled_catalog_matches_fixture():
    parsed = cat.parse_docs_markdown(FIXTURE.read_text(encoding="utf-8"))
    bundled = cat.load_catalog()
    assert bundled["fetched"] == "2026-11-27"
    for api, server in parsed["servers"].items():
        b = bundled["servers"][api]
        assert b["endpoint"] == server["endpoint"]
        for name, info in server["tools"].items():
            assert b["tools"][name]["toolsets"] == info["toolsets"]
            assert b["tools"][name]["access"] == info["access"]


def test_reference_links_are_web_pages():
    bundled = cat.load_catalog()
    for api, server in bundled["servers"].items():
        for name, info in server["tools"].items():
            ref = info["reference"]
            assert ref.startswith("https://developers.google.com/"), (api, name)
            assert ref.endswith("/" + name), (api, name)


def test_every_mapped_tool_exists_in_bundled_catalog():
    bundled = cat.load_catalog()
    for api, table in mapping.MAPPING.items():
        for key, (status, tools, note) in table.items():
            assert status in ("direct", "partial", "none"), key
            if status == "none":
                assert tools == [], key
            else:
                assert tools, key
            for t in tools:
                a, name = t.split(":", 1) if ":" in t else (api, t)
                assert cat.tool_info(bundled, a, name), f"{api} {key} -> {t}"


def test_self_mode_rules():
    c = cat.load_catalog()
    assert not cat.in_self_mode(c, "gmail", "send_message")
    assert cat.in_self_mode(c, "gmail", "create_draft")
    # People has no self-mode endpoint and no elicitation, so its tools count.
    assert cat.in_self_mode(c, "people", "search_contacts")
    assert not cat.in_self_mode(c, "gmail", "no_such_tool")


def test_parse_rejects_wrong_page():
    import pytest
    with pytest.raises(ValueError):
        cat.parse_docs_markdown("# Some other page\n\nno tables here\n")


def test_lookup_exact_beats_wildcard():
    assert mapping.lookup("gmail", "users.settings.filters.create")[0] == "direct"
    assert mapping.lookup("gmail", "users.settings.sendAs.list")[0] == "none"
    assert mapping.lookup("gmail", "users.settings.getVacation")[0] == "none"
    assert mapping.lookup("chat", "spaces.messages.list")[0] == "direct"
    assert mapping.lookup("gmail", "users.nothing") is None
    assert mapping.lookup("nope", "x.y") is None
