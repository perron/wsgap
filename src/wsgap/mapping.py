"""REST method -> Workspace MCP tool mapping.

Keys are Google discovery method paths (the same names the Python, Node,
Go and Java client libraries use), for example "users.messages.send".
A "*" segment matches any single segment.

Status values:
  direct   one MCP tool does what this REST method does.
  partial  the closest MCP tool covers part of it; read the note.
  none     no MCP tool in the catalog does this.

Tool names refer to the same API's MCP server unless written "api:tool".
Every mapping was written by hand from the tool reference pages on
developers.google.com (Nov 27 2026). Tests check that each named tool
exists in the bundled catalog.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

D, P, N = "direct", "partial", "none"

Entry = Tuple[str, List[str], str]

MAPPING: Dict[str, Dict[str, Entry]] = {
    "gmail": {
        "users.getProfile": (P, ["people:get_user_profile"], "No Gmail tool returns the mailbox profile. The People API tool returns your name and email, not message counts or historyId."),
        "users.watch": (N, [], "No push notifications through MCP."),
        "users.stop": (N, [], "No push notifications through MCP."),
        "users.messages.list": (P, ["search_threads"], "Returns threads, not single messages. Use get_thread to reach messages."),
        "users.messages.get": (D, ["get_message"], "Attachment ids and metadata come back; attachment bytes do not."),
        "users.messages.send": (P, ["send_message"], "send_message takes to, subject, body, htmlBody and attachments, not a raw MIME message. Replies and forwards have their own tools: reply and forward."),
        "users.messages.modify": (P, ["update_message_labels", "trash_message", "mark_message_spam"], "update_message_labels can't add or remove TRASH or SPAM; use trash_message or mark_message_spam for those."),
        "users.messages.trash": (D, ["trash_message"], ""),
        "users.messages.untrash": (D, ["untrash_message"], ""),
        "users.messages.delete": (N, [], "Permanent delete has no tool. trash_message only moves to Trash."),
        "users.messages.batchModify": (P, ["update_message_labels"], "One message per call."),
        "users.messages.batchDelete": (N, [], "Permanent delete has no tool."),
        "users.messages.insert": (N, [], ""),
        "users.messages.import": (N, [], ""),
        "users.messages.attachments.get": (N, [], "No tool downloads attachment data. get_message lists attachment ids and metadata only."),
        "users.threads.list": (P, ["search_threads"], "Drafts are always excluded (use list_drafts), pageSize is at most 50, and label: takes the label's display name, not its id."),
        "users.threads.get": (D, ["get_thread"], ""),
        "users.threads.modify": (P, ["label_thread", "unlabel_thread"], "Adding and removing labels are separate calls."),
        "users.threads.trash": (D, ["trash_thread"], ""),
        "users.threads.untrash": (D, ["untrash_thread"], ""),
        "users.threads.delete": (N, [], "Permanent delete has no tool. trash_thread only moves to Trash."),
        "users.drafts.create": (D, ["create_draft"], ""),
        "users.drafts.get": (D, ["get_draft"], ""),
        "users.drafts.list": (D, ["list_drafts"], ""),
        "users.drafts.update": (D, ["update_draft"], "update_draft merges fields instead of replacing the whole draft."),
        "users.drafts.send": (D, ["send_message"], "Pass draftId to send_message."),
        "users.drafts.delete": (N, [], ""),
        "users.labels.create": (D, ["create_label"], ""),
        "users.labels.list": (D, ["list_labels"], ""),
        "users.labels.get": (P, ["list_labels"], "No single-label get; list and pick."),
        "users.labels.update": (D, ["update_label"], ""),
        "users.labels.patch": (D, ["update_label"], ""),
        "users.labels.delete": (N, [], ""),
        "users.history.list": (N, [], "No history or sync tool."),
        "users.settings.filters.create": (D, ["create_filter"], "Needs the gmail.settings.basic or gmail.settings.filters scope."),
        "users.settings.filters.list": (D, ["list_filters"], ""),
        "users.settings.filters.get": (P, ["list_filters"], "No single-filter get; list and pick."),
        "users.settings.filters.delete": (N, [], ""),
        "users.settings.*": (N, [], "No settings tools besides filters (no vacation, send-as, forwarding, IMAP/POP, delegates)."),
        "users.settings.*.*": (N, [], "No settings tools besides filters (no vacation, send-as, forwarding, IMAP/POP, delegates)."),
    },
    "drive": {
        "files.list": (P, ["search_files", "list_recent_files"], "search_files has its own query syntax (title, parentId, ancestors), not Drive's q (name, 'id' in parents). list_recent_files only lists by recency."),
        "files.get": (D, ["get_file_metadata", "download_file_content"], "get_file_metadata for metadata; download_file_content for alt=media."),
        "files.create": (D, ["create_file"], ""),
        "files.copy": (D, ["copy_file"], ""),
        "files.update": (P, ["update_file", "upload_file_revision", "trash_file"], "update_file changes title, parentId (move), description, star and lock. New content goes through upload_file_revision (non-Google files only). Setting trashed: true is trash_file."),
        "files.delete": (N, [], "Permanent delete has no tool. trash_file only moves to Trash."),
        "files.emptyTrash": (N, [], ""),
        "files.export": (D, ["download_file_content"], "Pass exportMimeType; without it Google files come back as plain text or CSV."),
        "files.download": (D, ["download_file_content"], ""),
        "files.get_media": (D, ["download_file_content"], "Python client helper for files.get with alt=media."),
        "files.export_media": (D, ["download_file_content"], "Python client helper for files.export. Pass exportMimeType; without it Google files come back as plain text or CSV."),
        # Drive API v2 names.
        "files.insert": (D, ["create_file"], "Drive v2 name for files.create."),
        "files.patch": (P, ["update_file", "upload_file_revision", "trash_file"], "update_file changes title, parentId (move), description, star and lock. Setting trashed: true is trash_file."),
        "files.touch": (N, [], "Drive v2 only."),
        "permissions.insert": (N, [], "Drive v2 name for permissions.create. No sharing tool."),
        "permissions.patch": (N, [], "No sharing tool."),
        "files.generateIds": (N, [], ""),
        "files.watch": (N, [], "No push notifications through MCP."),
        "files.listLabels": (N, [], ""),
        "files.modifyLabels": (N, [], ""),
        "permissions.list": (D, ["get_file_permissions"], ""),
        "permissions.get": (P, ["get_file_permissions"], "Lists all permissions; pick the one you need."),
        "permissions.create": (N, [], "No sharing tool. request_access only asks the owner for access."),
        "permissions.update": (N, [], "No sharing tool."),
        "permissions.delete": (N, [], "No sharing tool."),
        "comments.list": (P, ["read_file_content"], "read_file_content can include comments; there is no comment API."),
        "comments.get": (P, ["read_file_content"], "read_file_content can include comments; there is no comment API."),
        "comments.create": (N, [], ""),
        "comments.update": (N, [], ""),
        "comments.delete": (N, [], ""),
        "replies.*": (N, [], "No comment reply tools."),
        "revisions.list": (D, ["list_file_revisions"], ""),
        "revisions.get": (P, ["list_file_revisions"], "Lists revisions; no single-revision get."),
        "revisions.update": (N, [], ""),
        "revisions.delete": (N, [], ""),
        "drives.list": (D, ["list_shared_drives"], ""),
        "drives.get": (D, ["get_shared_drive_metadata"], ""),
        "drives.create": (N, [], "No shared drive management."),
        "drives.update": (N, [], "No shared drive management."),
        "drives.delete": (N, [], "No shared drive management."),
        "drives.hide": (N, [], "No shared drive management."),
        "drives.unhide": (N, [], "No shared drive management."),
        "changes.*": (N, [], "No change feed through MCP."),
        "about.get": (N, [], ""),
        "accessproposals.*": (N, [], ""),
        "apps.*": (N, [], ""),
    },
    "calendar": {
        "events.list": (P, ["list_events"], "Without an end time list_events covers 7 days from the start, and its schema has no singleEvents option. For keyword search on the primary calendar, Google points to search_events."),
        "events.get": (D, ["get_event"], ""),
        "events.insert": (D, ["create_event"], ""),
        "events.update": (D, ["update_event"], "To RSVP, respond_to_event is simpler."),
        "events.patch": (D, ["update_event"], "To RSVP, respond_to_event is simpler."),
        "events.delete": (D, ["delete_event"], ""),
        "events.quickAdd": (P, ["create_event"], "No natural-language quick add; build the event yourself."),
        "events.instances": (N, [], ""),
        "events.move": (N, [], ""),
        "events.import": (N, [], ""),
        "events.watch": (N, [], "No push notifications through MCP."),
        "calendarList.list": (D, ["list_calendars"], ""),
        "calendarList.*": (N, [], "Only listing calendars is supported."),
        "calendars.*": (N, [], "No tools to create, change or delete calendars."),
        "acl.*": (N, [], "No calendar sharing tools."),
        "freebusy.query": (P, ["suggest_time"], "suggest_time returns free slots, not raw busy blocks."),
        "settings.*": (N, [], ""),
        "colors.get": (N, [], ""),
    },
    "docs": {
        "documents.get": (D, ["read_doc"], ""),
        "documents.batchUpdate": (D, ["update_doc"], ""),
        "documents.create": (P, ["drive:create_file"], "No Docs create tool. Drive create_file can create the file; check its schema for the type you need."),
    },
    "sheets": {
        "spreadsheets.get": (D, ["get_spreadsheet"], ""),
        "spreadsheets.create": (P, ["drive:create_file"], "No Sheets create tool. Drive create_file can create the file; check its schema for the type you need."),
        "spreadsheets.batchUpdate": (D, ["update_spreadsheet"], "insert_dimension is a shortcut for inserting rows or columns."),
        "spreadsheets.getByDataFilter": (N, [], ""),
        "spreadsheets.values.get": (D, ["get_values"], ""),
        "spreadsheets.values.batchGet": (P, ["get_values"], "One range per call."),
        "spreadsheets.values.update": (P, ["update_values", "update_formulas"], "update_values takes only booleans, strings and numbers. Formulas go through update_formulas."),
        "spreadsheets.values.batchUpdate": (P, ["update_values"], "One range per call."),
        "spreadsheets.values.append": (D, ["append_values"], ""),
        "spreadsheets.values.clear": (D, ["batch_clear_values"], ""),
        "spreadsheets.values.batchClear": (D, ["batch_clear_values"], ""),
        "spreadsheets.values.*": (N, [], ""),
        "spreadsheets.sheets.copyTo": (D, ["copy_sheet_to_another_spreadsheet"], ""),
        "spreadsheets.developerMetadata.*": (N, [], ""),
    },
    "slides": {
        "presentations.get": (D, ["read_presentation"], ""),
        "presentations.batchUpdate": (D, ["update_presentation"], ""),
        "presentations.create": (P, ["drive:create_file"], "No Slides create tool. Drive create_file can create the file; check its schema for the type you need."),
        "presentations.pages.get": (D, ["read_slide_page"], ""),
        "presentations.pages.getThumbnail": (D, ["read_slide_page_thumbnail"], ""),
    },
    "chat": {
        "spaces.messages.create": (D, ["send_message"], "Needs a Chat app configured in your Cloud project."),
        "spaces.messages.list": (D, ["list_messages"], ""),
        "spaces.messages.get": (P, ["list_messages", "search_messages"], "No single-message get."),
        "spaces.messages.update": (N, [], ""),
        "spaces.messages.patch": (N, [], ""),
        "spaces.messages.delete": (N, [], ""),
        "spaces.messages.*.*": (N, [], "No reaction or attachment tools."),
        "spaces.members.list": (D, ["list_memberships"], ""),
        "spaces.members.*": (N, [], "Only listing members is supported."),
        "spaces.list": (P, ["search_conversations"], "Search by name or participants; no plain list."),
        "spaces.search": (P, ["search_conversations"], ""),
        "spaces.get": (P, ["search_conversations"], "No single-space get."),
        "spaces.findDirectMessage": (P, ["search_conversations"], "Find DMs by participant email."),
        "spaces.*": (N, [], "No space administration tools."),
        "users.spaces.spaceNotificationSetting.get": (D, ["get_notification_settings"], ""),
        "users.spaces.spaceNotificationSetting.patch": (D, ["update_notification_settings"], ""),
        "users.spaces.updateSpaceReadState": (P, ["mark_as_read", "mark_as_unread"], ""),
        "users.spaces.getSpaceReadState": (N, [], ""),
        "users.spaces.threads.getThreadReadState": (N, [], ""),
        "media.*": (N, [], "No attachment upload or download."),
    },
    "tasks": {
        "tasklists.list": (D, ["list_task_lists"], ""),
        "tasklists.*": (N, [], "Only listing task lists is supported."),
        "tasks.list": (D, ["list_tasks"], ""),
        "tasks.get": (D, ["get_task"], ""),
        "tasks.insert": (D, ["create_task"], ""),
        "tasks.update": (P, ["update_task", "complete_task", "uncomplete_task"], "Changing completion is a separate call: complete_task or uncomplete_task."),
        "tasks.patch": (P, ["update_task", "complete_task", "uncomplete_task"], "Changing completion is a separate call: complete_task or uncomplete_task."),
        "tasks.delete": (D, ["delete_task"], ""),
        "tasks.move": (N, [], ""),
        "tasks.clear": (N, [], ""),
    },
    "people": {
        "people.get": (P, ["get_user_profile"], "Only your own profile (people/me), name and email."),
        "people.searchContacts": (D, ["search_contacts"], ""),
        "people.searchDirectoryPeople": (D, ["search_directory_people"], "Workspace accounts only."),
        "people.connections.list": (P, ["search_contacts"], "Search only; no full contact list."),
        "people.*": (N, [], "No contact create, update or delete tools."),
        "contactGroups.*": (N, [], ""),
        "contactGroups.*.*": (N, [], ""),
        "otherContacts.*": (N, [], ""),
    },
}

# Method names the client libraries use for "create" on a collection.
CREATE_NAMES = ("create", "insert")


def lookup(api: str, method: str) -> Optional[Entry]:
    """Return the mapping entry for api + method path, or None if unknown.

    Exact keys win over wildcard keys.
    """
    table = MAPPING.get(api)
    if not table:
        return None
    if method in table:
        return table[method]
    parts = method.split(".")
    best = None
    best_score = -1
    for key, entry in table.items():
        kparts = key.split(".")
        if len(kparts) != len(parts):
            continue
        score = 0
        ok = True
        for k, p in zip(kparts, parts):
            if k == p:
                score += 1
            elif k != "*":
                ok = False
                break
        if ok and score > best_score:
            best, best_score = entry, score
    return best


def known_methods(api: str) -> List[str]:
    return [k for k in MAPPING.get(api, {}) if "*" not in k]
