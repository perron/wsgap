"""Turn a Workspace REST URL into a discovery method path.

Only the path is used. When the path doesn't name the method (for example
GET vs POST on a collection), the HTTP verb found near the URL decides it;
without a verb the result lists the candidate methods.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

# host -> list of (path prefix, api). Prefixes are matched in order.
PREFIXES: List[Tuple[str, str, str]] = [
    # (host, prefix, api)
    ("gmail", "/gmail/v1/", "gmail"),
    ("gmail", "/upload/gmail/v1/", "gmail"),
    ("www", "/gmail/v1/", "gmail"),
    ("www", "/upload/gmail/v1/", "gmail"),
    ("www", "/drive/v3/", "drive"),
    ("www", "/drive/v2/", "drive"),
    ("www", "/upload/drive/v2/", "drive"),
    ("www", "/upload/drive/v3/", "drive"),
    ("drive", "/drive/v3/", "drive"),
    ("drive", "/upload/drive/v3/", "drive"),
    ("www", "/calendar/v3/", "calendar"),
    ("calendar", "/calendar/v3/", "calendar"),
    ("www", "/tasks/v1/", "tasks"),
    ("tasks", "/tasks/v1/", "tasks"),
    ("sheets", "/v4/", "sheets"),
    ("docs", "/v1/", "docs"),
    ("slides", "/v1/", "slides"),
    ("chat", "/v1/", "chat"),
    ("people", "/v1/", "people"),
]

# Collections per API, in URL form. Value: discovery resource name.
COLLECTIONS: Dict[str, Dict[str, str]] = {
    "gmail": {s: s for s in ["users", "messages", "threads", "drafts", "labels", "history",
                             "settings", "filters", "sendAs", "forwardingAddresses",
                             "delegates", "attachments", "smimeInfo", "cse", "identities", "keypairs"]},
    "drive": {s: s for s in ["files", "permissions", "comments", "replies", "revisions",
                             "drives", "changes", "about", "accessproposals", "apps", "channels"]},
    "calendar": {"calendars": "calendars", "events": "events", "acl": "acl", "users": "users",
                 "calendarList": "calendarList", "settings": "settings", "colors": "colors",
                 "freeBusy": "freebusy", "channels": "channels"},
    "tasks": {"users": "users", "lists": "lists", "tasks": "tasks"},
    "sheets": {"spreadsheets": "spreadsheets", "values": "values", "sheets": "sheets",
               "developerMetadata": "developerMetadata"},
    "docs": {"documents": "documents"},
    "slides": {"presentations": "presentations", "pages": "pages"},
    "chat": {"spaces": "spaces", "messages": "messages", "members": "members",
             "reactions": "reactions", "attachments": "attachments", "users": "users",
             "spaceEvents": "spaceEvents", "threads": "threads", "media": "media"},
    "people": {"people": "people", "connections": "connections", "contactGroups": "contactGroups",
               "otherContacts": "otherContacts", "members": "members"},
}

# Custom verbs that appear as a final path segment (Gmail, Drive, Calendar, Tasks)
# or after a colon (Sheets, Docs, Slides, Chat, People).
VERBS: Dict[str, Dict[str, str]] = {
    "gmail": {"send": "send", "modify": "modify", "trash": "trash", "untrash": "untrash",
              "batchModify": "batchModify", "batchDelete": "batchDelete", "import": "import",
              "watch": "watch", "stop": "stop", "profile": "getProfile"},
    "drive": {"copy": "copy", "export": "export", "generateIds": "generateIds",
              "emptyTrash": "emptyTrash", "watch": "watch", "listLabels": "listLabels",
              "modifyLabels": "modifyLabels", "download": "download", "hide": "hide",
              "unhide": "unhide", "startPageToken": "getStartPageToken", "stop": "stop"},
    "calendar": {"quickAdd": "quickAdd", "move": "move", "instances": "instances",
                 "import": "import", "watch": "watch", "clear": "clear", "stop": "stop"},
    "tasks": {"clear": "clear", "move": "move"},
    "sheets": {"batchUpdate": "batchUpdate", "append": "append", "clear": "clear",
               "batchGet": "batchGet", "batchClear": "batchClear", "copyTo": "copyTo",
               "getByDataFilter": "getByDataFilter", "batchGetByDataFilter": "batchGetByDataFilter",
               "batchUpdateByDataFilter": "batchUpdateByDataFilter",
               "batchClearByDataFilter": "batchClearByDataFilter", "search": "search"},
    "docs": {"batchUpdate": "batchUpdate"},
    "slides": {"batchUpdate": "batchUpdate", "thumbnail": "getThumbnail"},
    "chat": {"setup": "setup", "search": "search", "findDirectMessage": "findDirectMessage",
             "completeImport": "completeImport", "upload": "upload"},
    "people": {"searchContacts": "searchContacts", "searchDirectoryPeople": "searchDirectoryPeople",
               "createContact": "createContact", "updateContact": "updateContact",
               "deleteContact": "deleteContact", "batchGet": "getBatchGet",
               "listDirectoryPeople": "listDirectoryPeople", "batchCreateContacts": "batchCreateContacts",
               "batchUpdateContacts": "batchUpdateContacts", "batchDeleteContacts": "batchDeleteContacts",
               "search": "search", "updateContactPhoto": "updateContactPhoto",
               "deleteContactPhoto": "deleteContactPhoto"},
}

# Walked resource path (tuple of URL collections) -> discovery resource path.
RENAMES: Dict[str, Dict[Tuple[str, ...], str]] = {
    "calendar": {("calendars", "events"): "events", ("calendars", "acl"): "acl",
                 ("users", "calendarList"): "calendarList", ("users", "settings"): "settings",
                 ("calendars",): "calendars", ("freebusy",): "freebusy", ("colors",): "colors",
                 ("channels",): "channels"},
    "tasks": {("users", "lists"): "tasklists", ("lists", "tasks"): "tasks", ("lists",): "tasklists"},
    "drive": {("files", "permissions"): "permissions", ("drives", "permissions"): "permissions",
              ("files", "comments"): "comments", ("files", "comments", "replies"): "replies",
              ("files", "revisions"): "revisions", ("files", "accessproposals"): "accessproposals"},
    "slides": {},
}

# Verbs that read like a method on the collection itself, for when the
# walk ends on a collection or a single item.
ON_COLLECTION = {"GET": ["list"], "POST": ["create", "insert"]}
ON_ITEM = {"GET": ["get"], "PUT": ["update"], "PATCH": ["patch", "update"], "DELETE": ["delete"]}

# Singleton resources: the last segment is the object itself, not a collection.
SINGLETON_GET = {
    ("drive", "about"): "about.get",
    ("calendar", "colors"): "colors.get",
}

URL_RE = re.compile(r"https?://(?P<host>[a-z]+)\.googleapis\.com(?P<path>/[^\s'\"`)<>\\,;]*)")


def split_url(host: str, path: str) -> Optional[Tuple[str, List[str], bool]]:
    """Return (api, path segments, is_upload_url) or None if not a known Workspace API."""
    for h, prefix, api in PREFIXES:
        if host == h and path.startswith(prefix):
            rest = path[len(prefix):].split("?", 1)[0].split("#", 1)[0]
            segs = [s for s in rest.split("/") if s]
            if rest.endswith("/") and segs:
                segs.append("{id}")  # "…/files/" + id: an item id is concatenated after the slash
            return api, segs, prefix.startswith("/upload/")
    return None


def parse_path(api: str, segs: List[str]) -> Optional[Dict]:
    """Return {"resource": "a.b", "verb": custom-verb or None, "ends_on": "collection"|"item"}."""
    if not segs:
        return None
    colls = COLLECTIONS[api]
    verbs = VERBS.get(api, {})
    custom = None
    # Colon verb on the last segment (Sheets, Docs, Slides, Chat, People).
    last = segs[-1]
    if ":" in last:
        head, _, tail = last.rpartition(":")
        if tail in verbs:
            custom = verbs[tail]
            segs = segs[:-1] + ([head] if head else [])
    walked: List[str] = []
    ends_on = None
    expect_collection = True
    for i, seg in enumerate(segs):
        is_last = i == len(segs) - 1
        if custom is None and is_last and seg in verbs and walked:
            custom = verbs[seg]
            break
        if expect_collection:
            if seg in colls:
                walked.append(colls[seg])
                ends_on = "collection"
                expect_collection = False
            else:
                return None
        else:
            ends_on = "item"
            expect_collection = True
    if not walked:
        return None
    key = tuple(walked)
    renames = RENAMES.get(api, {})
    if key in renames:
        resource = renames[key]
    else:
        resource = ".".join(walked)
    if api == "gmail" and resource == "users" and custom is None:
        # /users/me alone is not a method we know.
        return None
    if api == "tasks" and resource == "users":
        return None
    return {"resource": resource, "verb": custom, "ends_on": ends_on}


def methods_for(api: str, parsed: Dict, http_verb: Optional[str], upload: bool = False) -> List[str]:
    """Candidate discovery method paths for a parsed URL."""
    res = parsed["resource"]
    if upload and not parsed["verb"] and not http_verb:
        # /upload/ URLs only take new content: create on a collection, update on an item.
        http_verb = "POST" if parsed["ends_on"] == "collection" else "PUT"
    if parsed["verb"]:
        if res == "users" and api == "gmail":
            return ["users." + parsed["verb"]]
        if api == "people" and parsed["verb"] in ("searchContacts", "searchDirectoryPeople",
                                                  "createContact", "listDirectoryPeople",
                                                  "getBatchGet", "batchCreateContacts",
                                                  "batchUpdateContacts", "batchDeleteContacts"):
            return ["people." + parsed["verb"]]
        if api == "chat" and res == "spaces" and parsed["verb"] in ("setup", "search", "findDirectMessage"):
            return ["spaces." + parsed["verb"]]
        if api == "drive" and parsed["verb"] == "getStartPageToken":
            return ["changes.getStartPageToken"]
        return [res + "." + parsed["verb"]]
    single = SINGLETON_GET.get((api, res))
    if single:
        return [single]
    if api == "calendar" and res == "freebusy":
        return ["freebusy.query"]
    if api == "people" and res == "people.connections":
        return ["people.connections.list"]
    table = ON_COLLECTION if parsed["ends_on"] == "collection" else ON_ITEM
    if http_verb and http_verb in table:
        return [res + "." + m for m in table[http_verb]]
    out: List[str] = []
    for ms in table.values():
        out.extend(res + "." + m for m in ms)
    return list(dict.fromkeys(out))


# Patterns that name the verb in the call itself, e.g. requests.post( or http.NewRequest("PUT".
_CALL_VERB = [
    re.compile(r"\b(?:requests|httpx|session|client|sess|http|axios|aiohttp|ky|got|superagent)\s*\.\s*(get|post|put|patch|delete)\s*\(", re.I),
    re.compile(r"\bhttp\.Method(Get|Post|Put|Patch|Delete)\b"),
    re.compile(r"NewRequest(?:WithContext)?\(\s*(?:ctx\s*,\s*)?\"(GET|POST|PUT|PATCH|DELETE)\""),
    re.compile(r"\brequest\s*\(\s*['\"](GET|POST|PUT|PATCH|DELETE)['\"]", re.I),
]
# Patterns that set the verb as an option, e.g. fetch(url, { method: "POST" }).
_OPTION_VERB = [
    re.compile(r"\bmethod\s*[:=]\s*['\"](GET|POST|PUT|PATCH|DELETE)['\"]", re.I),
]
# Shell: curl -X POST / --request POST, PowerShell -Method Post.
_SHELL_VERB = [
    re.compile(r"(?:-X|--request)\s*['\"]?(GET|POST|PUT|PATCH|DELETE)\b"),
    re.compile(r"-Method\s+['\"]?(Get|Post|Put|Patch|Delete)\b", re.I),
]
_CURL_DATA = re.compile(r"(?:^|\s)(?:-d|--data(?:-raw|-binary|-urlencode)?|-F|--form|--json|-T|--upload-file)(?:\s|=|$)")


def _verbs(texts: List[str], pats) -> set:
    found = set()
    for text in texts:
        for pat in pats:
            for m in pat.finditer(text):
                found.add(m.group(1).upper())
    return found


def find_http_verb(lines: List[str], idx: int, shell: bool = False) -> Optional[str]:
    """Find the HTTP verb for a URL on line idx, or None if it can't be told.

    Shell: the whole backslash-continued command is used; curl with no -X
    means GET, or POST when it sends data.
    Code: the URL's line, then up to four lines before it in the same
    statement for a call such as requests.post(, then the three lines after
    it for a method: option.
    """
    if shell:
        lo = idx
        while lo > 0 and lines[lo - 1].rstrip().endswith(("\\", "`")):
            lo -= 1
        hi = idx
        while hi < len(lines) - 1 and lines[hi].rstrip().endswith(("\\", "`")):
            hi += 1
        cmd = lines[lo:hi + 1]
        found = _verbs(cmd, _SHELL_VERB)
        if len(found) == 1:
            return found.pop()
        if found:
            return None
        joined = " ".join(cmd)
        if re.search(r"\bcurl\b", joined):
            return "POST" if _CURL_DATA.search(joined) else "GET"
        return None
    same = _verbs([lines[idx]], _CALL_VERB + _OPTION_VERB + _SHELL_VERB)
    if len(same) == 1:
        return same.pop()
    if same:
        return None
    # Walk back through the same statement (lines that don't end it) for a call verb.
    for j in range(idx - 1, max(-1, idx - 5), -1):
        prev = lines[j].strip()
        if not prev or prev.endswith((")", ";", "}")):
            break
        found = _verbs([lines[j]], _CALL_VERB)
        if len(found) == 1:
            return found.pop()
        if found:
            return None
    after = _verbs(lines[idx + 1:idx + 4], _OPTION_VERB)
    if len(after) == 1:
        return after.pop()
    return None
