from wsgap import scanner


def methods(text, path="x.py"):
    return [(f.api, f.method) for f in scanner.scan_text(text, path)]


def test_python_chain_and_trailing_execute():
    src = 'from googleapiclient.discovery import build\nsvc = build("gmail", "v1")\nsvc.users().messages().send(userId="me", body=b).execute()\n'
    assert methods(src) == [("gmail", "users.messages.send")]


def test_python_empty_args_method_then_execute():
    src = 'cal = build("calendar", "v3")\ncal.calendarList().list().execute()\n'
    assert methods(src) == [("calendar", "calendarList.list")]


def test_python_multiline_chain_reports_first_line():
    src = "x = (\n    service.users()\n    .messages()\n    .attachments()\n    .get(userId='me', messageId=m, id=a)\n    .execute()\n)\n"
    f = scanner.scan_text(src, "x.py")
    assert [(x.method, x.line) for x in f] == [("users.messages.attachments.get", 2)]


def test_python_helper_without_import_still_found_for_long_paths():
    src = "def f(service):\n    return service.users().threads().list(userId='me').execute()\n"
    assert methods(src) == [("gmail", "users.threads.list")]


def test_two_segment_paths_need_evidence():
    # Plain Python list/dict calls must not count.
    src = "tasks = []\ntasks.insert(0, x)\nevents.update(other)\nvalues.get('a')\nfiles.update(y)\n"
    assert methods(src) == []
    # Discovery style with a unique Workspace resource does count, even without an import.
    assert methods("def f(service):\n    service.files().list(q='x').execute()\n") == [("drive", "files.list")]


def test_other_google_api_is_ignored():
    src = ('from googleapiclient.discovery import build\n'
           'yt = build("youtube", "v3")\n'
           'yt.comments().list(part="snippet").execute()\n'
           'db.projects().databases().documents().get(name=n).execute()\n')
    assert methods(src) == []


def test_mock_attribute_access_is_not_a_wildcard_method():
    src = "kw = chat_service.spaces().messages().list.call_args.kwargs\nchat_service.spaces().messages().list(parent=p)\n"
    assert methods(src) == [("chat", "spaces.messages.list")]


def test_node_googleapis():
    src = ('import { google } from "googleapis";\n'
           'const drive = google.drive({ version: "v3", auth });\n'
           'await drive.files.create({ requestBody: {} });\n'
           'await drive.permissions.create({ fileId: id });\n'
           'await sheetsApi.spreadsheets.values.append({});\n')
    assert methods(src, "a.ts") == [
        ("drive", "files.create"), ("drive", "permissions.create"), ("sheets", "spreadsheets.values.append")]


def test_go_client():
    src = ('import tasks "google.golang.org/api/tasks/v1"\n'
           'srv, err := tasks.NewService(ctx)\n'
           'srv.Tasks.Insert(listID, &tasks.Task{}).Do()\n'
           'srv.Tasklists.List().Do()\n')
    assert methods(src, "a.go") == [("tasks", "tasks.insert"), ("tasks", "tasklists.list")]


def test_java_client():
    src = ('import com.google.api.services.gmail.Gmail;\n'
           'Gmail service = new Gmail.Builder(t, j, c).build();\n'
           'service.users().labels().list("me").execute();\n')
    assert methods(src, "A.java") == [("gmail", "users.labels.list")]


def test_bound_to_other_api_blocks_match():
    src = 'gmail = build("gmail", "v1")\ngmail.files().list().execute()\n'
    assert methods(src) == []


def test_urls_custom_verbs_and_ranges():
    src = ('u1 = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"\n'
           'u2 = f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/Log!A1:C3:append"\n'
           'u3 = "https://people.googleapis.com/v1/people:searchContacts?query=x"\n'
           'u4 = "https://www.googleapis.com/calendar/v3/users/me/calendarList"\n'
           'u5 = "https://slides.googleapis.com/v1/presentations/P/pages/G/thumbnail"\n'
           'scope = "https://www.googleapis.com/auth/gmail.send"\n')
    got = methods(src)
    assert ("gmail", "users.messages.send") in got
    assert ("sheets", "spreadsheets.values.append") in got
    assert ("people", "people.searchContacts") in got
    assert ("slides", "presentations.pages.getThumbnail") in got
    # calendarList with no verb: list (GET) or insert (POST); first candidate is list.
    assert ("calendar", "calendarList.list") in got
    assert len(got) == 5  # the OAuth scope URL is not an API call


def test_url_verbs_from_code():
    src = ('r = requests.delete(\n'
           '    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}",\n'
           ')\n'
           'fetch("https://www.googleapis.com/drive/v3/files/" + id, {\n'
           '  method: "PATCH",\n'
           '})\n')
    f = scanner.scan_text(src, "a.py")
    assert [(x.method, x.http_verb) for x in f] == [("users.messages.delete", "DELETE"), ("files.patch", "PATCH")]


def test_url_verbs_from_shell():
    src = ('curl -s -H "A: b" \\\n'
           '  "https://gmail.googleapis.com/gmail/v1/users/me/drafts"\n'
           'curl -s -X DELETE \\\n'
           '  "https://gmail.googleapis.com/gmail/v1/users/me/labels/L1"\n'
           'curl -s -d @body.json "https://www.googleapis.com/calendar/v3/calendars/primary/events"\n')
    f = scanner.scan_text(src, "a.sh")
    assert [(x.method, x.http_verb) for x in f] == [
        ("users.drafts.list", "GET"), ("users.labels.delete", "DELETE"), ("events.insert", "POST")]


def test_upload_url_means_create_or_update():
    src = ('A = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"\n'
           'B = f"https://www.googleapis.com/upload/drive/v3/files/{fid}?uploadType=media"\n')
    f = scanner.scan_text(src, "a.py")
    assert [x.method for x in f] == ["files.create", "files.update"]


def test_exclude_and_skip_dirs(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "node_modules").mkdir()
    code = 'svc.users().messages().send(userId="me").execute()\n'
    (tmp_path / "app.py").write_text(code)
    (tmp_path / "tests" / "test_app.py").write_text(code)
    (tmp_path / "node_modules" / "x.js").write_text(code)
    (tmp_path / "notes.md").write_text(code)
    found, n = scanner.scan_paths([str(tmp_path)])
    assert n == 2 and len(found) == 2
    found, n = scanner.scan_paths([str(tmp_path)], exclude=["tests/*"])
    assert n == 1 and found[0].path.endswith("app.py")
