Browse all toolsets and tools across the generally available Google Workspace
Model Context Protocol (MCP) servers in a single reference guide.

This reference guide brings together all toolsets and tools for the nine
generally available Google Workspace
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)
servers on a single page: Gmail, Google Drive, Google Docs,
Google Sheets, Google Slides, Google Calendar, Google Chat,
Google Tasks, and the People API.

Each product also maintains its own setup guide and generated MCP reference
with full input and output JSON schemas, `curl` request samples, tool
annotations, and OAuth 2.0 authorization scopes. Select any tool name on this
page to open its complete generated reference documentation.

> [!NOTE]
> **Note:** The Google Classroom and [Universal Search](https://developers.google.com/workspace/guides/universal-search-mcp.md.txt) MCP servers require enrollment in the [Google Workspace Developer Preview Program](https://developers.google.com/workspace/preview.md.txt) and aren't listed on this page. For links to those servers and their tool references, see [Supported products](https://developers.google.com/workspace/guides/configure-mcp-servers.md.txt#support-products).

## Toolset endpoints

Most generally available Google Workspace MCP servers expose two
toolset endpoints. The People API MCP server exposes only the
`/mcp/v1` endpoint and doesn't use form elicitation:

- **`/mcp/v1`** : Primary toolset endpoint. Exposes all tools for the server, including actions that require user confirmation through [MCP form elicitation](https://developers.google.com/workspace/guides/mcp-elicitation.md.txt). Use this endpoint whenever your MCP host or client supports form elicitation.
- **`/mcp/v1self`**: Fallback self-mode toolset endpoint for MCP hosts and clients that don't support form elicitation. Omits tools that always require interactive approval under default policy. List and search tools on this endpoint return only items accessible without approval.

The following table summarizes all nine generally available
Google Workspace MCP servers, their base URLs, their tool counts per
toolset, and links to their setup guides and generated reference overviews:

| Product toolset | Base server URL | `/mcp/v1` | `/mcp/v1self` | Setup and reference |
|---|---|---|---|---|
| [Gmail](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#gmail) | `https://gmailmcp.googleapis.com` | 30 tools | 25 tools | [Setup](https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/gmail/api/reference/mcp.md.txt) |
| [Drive](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#drive) | `https://drivemcp.googleapis.com` | 15 tools | 12 tools | [Setup](https://developers.google.com/workspace/drive/api/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/drive/api/reference/mcp.md.txt) |
| [Docs](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#docs) | `https://docsmcp.googleapis.com` | 2 tools | 2 tools | [Setup](https://developers.google.com/workspace/docs/api/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/docs/api/reference/mcp.md.txt) |
| [Sheets](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#sheets) | `https://sheetsmcp.googleapis.com` | 9 tools | 9 tools | [Setup](https://developers.google.com/workspace/sheets/api/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/sheets/api/reference/mcp.md.txt) |
| [Slides](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#slides) | `https://slidesmcp.googleapis.com` | 4 tools | 4 tools | [Setup](https://developers.google.com/workspace/slides/api/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/slides/api/reference/mcp.md.txt) |
| [Calendar](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#calendar) | `https://calendarmcp.googleapis.com` | 9 tools | 8 tools | [Setup](https://developers.google.com/workspace/calendar/api/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/calendar/api/v3/reference/mcp.md.txt) |
| [Chat](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#chat) | `https://chatmcp.googleapis.com` | 9 tools | 8 tools | [Setup](https://developers.google.com/workspace/chat/api/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/chat/api/reference/mcp.md.txt) |
| [Tasks](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#tasks) | `https://tasksmcp.googleapis.com` | 9 tools | 8 tools | [Setup](https://developers.google.com/workspace/tasks/guides/configure-mcp-server.md.txt), [Reference](https://developers.google.com/workspace/tasks/reference/mcp) |
| [People API](https://developers.google.com/workspace/guides/mcp-server-tools.md.txt#people) | `https://people.googleapis.com` | 3 tools | Not applicable | [Setup](https://developers.google.com/people/v1/configure-mcp-server.md.txt), [Reference](https://developers.google.com/people/api/mcp.md.txt) |

## Gmail toolsets

The Gmail MCP server lets AI agents search and read threads,
messages, drafts, labels, and filters, send and forward emails, manage drafts,
and organize mailboxes. For setup instructions and full schemas, see
[Configure the Gmail MCP server](https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server.md.txt) and the
[Gmail MCP reference](https://developers.google.com/workspace/gmail/api/reference/mcp.md.txt).

The Gmail MCP server provides the following toolset endpoints:

- Primary endpoint: `https://gmailmcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://gmailmcp.googleapis.com/mcp/v1self`

> [!NOTE]
> **Note:** Calling `create_filter` requires either the `https://www.googleapis.com/auth/gmail.settings.basic` or `https://www.googleapis.com/auth/gmail.settings.filters` OAuth scope.

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`apply_sensitive_message_label`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/apply_sensitive_message_label) | Moves a single message to Trash or Spam. Prefer `trash_message` or `mark_message_spam` instead. | Write | `/mcp/v1` only |
| [`apply_sensitive_thread_label`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/apply_sensitive_thread_label) | Moves an entire thread to Trash or Spam. Prefer `trash_thread` or `mark_thread_spam` instead. | Write | `/mcp/v1` only |
| [`create_draft`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/create_draft.md.txt) | Creates a new draft email or draft reply in the user's Gmail account. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`create_filter`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/create_filter.md.txt) | Creates an email filter and routing rule in the user's Gmail account. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`create_label`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/create_label.md.txt) | Creates a label in the user's Gmail account, including nested sub-labels separated by `/`. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`forward`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/forward.md.txt) | Forwards an email message with optional plain-text or HTML comments and attachments. | Write | `/mcp/v1` only |
| [`get_draft`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/get_draft) | Retrieves a specific draft email by ID, including its web `viewUrl`. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`get_message`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/get_message.md.txt) | Retrieves a single email message by ID, including its web `viewUrl`. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`get_thread`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/get_thread.md.txt) | Retrieves a full email thread and its messages by ID, including web `viewUrl` links. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`label_message`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/label_message.md.txt) | Adds one or more labels to a specific message. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`label_thread`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/label_thread.md.txt) | Adds one or more labels to an entire thread and future messages in that thread. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`list_drafts`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/list_drafts.md.txt) | Lists draft emails, optionally filtered by a search query. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_filters`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/list_filters.md.txt) | Lists user-defined email filters and routing rules. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_labels`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/list_labels.md.txt) | Lists all system and user labels along with each label's ID and display name. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`mark_message_spam`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/mark_message_spam) | Marks a single message as Spam. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`mark_thread_spam`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/mark_thread_spam) | Marks all messages in a thread as Spam. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`reply`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/reply.md.txt) | Replies to an email message sender or to all recipients using `replyAll`. | Write | `/mcp/v1` only |
| [`search_threads`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/search_threads.md.txt) | Searches and lists email threads in the user's Gmail account. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`send_message`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/send_message.md.txt) | Sends a new email message immediately from the user's Gmail account. | Write | `/mcp/v1` only |
| [`trash_message`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/trash_message) | Moves a single message to Trash without permanently deleting it. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`trash_thread`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/trash_thread) | Moves an entire thread to Trash without permanently deleting it. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`unlabel_message`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/unlabel_message.md.txt) | Removes one or more labels from a specific message. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`unlabel_thread`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/unlabel_thread.md.txt) | Removes one or more labels from an entire thread. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`unmark_message_spam`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/unmark_message_spam) | Removes the Spam label from a single message. Add the `INBOX` label separately to return it to the Inbox. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`unmark_thread_spam`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/unmark_thread_spam) | Removes the Spam label from an entire thread. Add the `INBOX` label separately to return it to the Inbox. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`untrash_message`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/untrash_message) | Removes a single message from Trash. Add the `INBOX` label separately to return it to the Inbox. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`untrash_thread`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/untrash_thread) | Removes an entire thread from Trash. Add the `INBOX` label separately to return it to the Inbox. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_draft`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/update_draft.md.txt) | Updates an existing draft email using merge semantics for fields other than attachments. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_label`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/update_label.md.txt) | Updates an existing label's name, color, and visibility settings. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_message_labels`](https://developers.google.com/workspace/gmail/api/reference/mcp/tools_list/update_message_labels) | Adds and removes labels on a single message in one atomic operation. | Write | `/mcp/v1`, `/mcp/v1self` |

## Drive toolsets

The Drive MCP server lets AI agents search files and shared
drives, read and download file content, inspect metadata, permissions, and
revisions, and create, copy, update, upload, or trash files. For setup
instructions, file eligibility details, and full schemas, see
[Configure the Drive MCP server](https://developers.google.com/workspace/drive/api/guides/configure-mcp-server.md.txt),
[Drive MCP file eligibility](https://developers.google.com/workspace/drive/api/guides/drive-mcp-server-file-eligibility.md.txt), and the
[Drive MCP reference](https://developers.google.com/workspace/drive/api/reference/mcp.md.txt).

The Drive MCP server provides the following toolset endpoints:

- Primary endpoint: `https://drivemcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://drivemcp.googleapis.com/mcp/v1self`

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`copy_file`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/copy_file.md.txt) | Copies an existing Drive file with an optional title and parent folder. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`create_file`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/create_file.md.txt) | Creates or uploads a new file or folder in Drive. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`download_file_content`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/download_file_content.md.txt) | Downloads a Drive file's content as a Base64-encoded string. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`get_file_metadata`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/get_file_metadata.md.txt) | Retrieves metadata for a Drive file. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`get_file_permissions`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/get_file_permissions.md.txt) | Lists access permissions for a Drive file. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`get_shared_drive_metadata`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/get_shared_drive_metadata.md.txt) | Retrieves metadata for a shared drive. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_file_revisions`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/list_file_revisions.md.txt) | Lists historical revisions of a Drive file. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_recent_files`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/list_recent_files.md.txt) | Lists recent files for the user in a specified sort order, defaulting to recency. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_shared_drives`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/list_shared_drives.md.txt) | Searches and lists shared drives using a structured query. | Read-only | `/mcp/v1` only |
| [`read_file_content`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/read_file_content.md.txt) | Retrieves a text representation of a Drive file and optionally its comments. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`request_access`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/request_access.md.txt) | Requests access to a Drive file. | Write | `/mcp/v1` only |
| [`search_files`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/search_files.md.txt) | Searches for Drive files using structured query terms and operators. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`trash_file`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/trash_file.md.txt) | Moves a Drive file to Trash without permanently deleting it. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_file`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/update_file.md.txt) | Updates a Drive file's metadata, or locks and unlocks the file. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`upload_file_revision`](https://developers.google.com/workspace/drive/api/reference/mcp/tools_list/upload_file_revision.md.txt) | Uploads a new content revision for an existing non-Google Workspace file in Drive. | Write | `/mcp/v1` only |

## Docs toolsets

The Docs MCP server lets AI agents read document content and
structure and apply batch updates to documents. For setup instructions and full
schemas, see [Configure the Docs MCP server](https://developers.google.com/workspace/docs/api/guides/configure-mcp-server.md.txt) and the
[Docs MCP reference](https://developers.google.com/workspace/docs/api/reference/mcp.md.txt).

The Docs MCP server provides the following toolset endpoints:

- Primary endpoint: `https://docsmcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://docsmcp.googleapis.com/mcp/v1self`

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`read_doc`](https://developers.google.com/workspace/docs/api/reference/mcp/tools_list/read_doc.md.txt) | Retrieves a JSON representation of a Docs document by document ID. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`update_doc`](https://developers.google.com/workspace/docs/api/reference/mcp/tools_list/update_doc.md.txt) | Applies `documents.batchUpdate` JSON requests to edit a Docs document. | Write | `/mcp/v1`, `/mcp/v1self` |

## Sheets toolsets

The Sheets MCP server lets AI agents read spreadsheets and cell
ranges, update, append, and clear values, set formulas, insert rows or columns,
copy sheets, and apply batch spreadsheet updates. For setup instructions and
full schemas, see [Configure the Sheets MCP server](https://developers.google.com/workspace/sheets/api/guides/configure-mcp-server.md.txt)
and the [Sheets MCP reference](https://developers.google.com/workspace/sheets/api/reference/mcp.md.txt).

The Sheets MCP server provides the following toolset endpoints:

- Primary endpoint: `https://sheetsmcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://sheetsmcp.googleapis.com/mcp/v1self`

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`append_values`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/append_values.md.txt) | Appends rows of values to a spreadsheet. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`batch_clear_values`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/batch_clear_values.md.txt) | Clears values from one or more ranges in a spreadsheet. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`copy_sheet_to_another_spreadsheet`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/copy_sheet_to_another_spreadsheet.md.txt) | Copies a single sheet from one spreadsheet to another spreadsheet. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`get_spreadsheet`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/get_spreadsheet.md.txt) | Retrieves spreadsheet titles, sheet names, grid properties, metadata, and optional full grid data. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`get_values`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/get_values.md.txt) | Retrieves a range of cell values from a spreadsheet. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`insert_dimension`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/insert_dimension.md.txt) | Inserts rows or columns in a sheet at a specified index. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_formulas`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/update_formulas.md.txt) | Sets formulas in a specified cell range of a spreadsheet. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_spreadsheet`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/update_spreadsheet.md.txt) | Applies one or more batch updates to a spreadsheet. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_values`](https://developers.google.com/workspace/sheets/api/reference/mcp/tools_list/update_values.md.txt) | Sets cell values in a specified range of a spreadsheet. | Write | `/mcp/v1`, `/mcp/v1self` |

## Slides toolsets

The Slides MCP server lets AI agents read presentations,
individual slides, and slide thumbnails, and apply batch updates to edit
presentations. For setup instructions and full schemas, see
[Configure the Slides MCP server](https://developers.google.com/workspace/slides/api/guides/configure-mcp-server.md.txt) and the
[Slides MCP reference](https://developers.google.com/workspace/slides/api/reference/mcp.md.txt).

The Slides MCP server provides the following toolset endpoints:

- Primary endpoint: `https://slidesmcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://slidesmcp.googleapis.com/mcp/v1self`

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`read_presentation`](https://developers.google.com/workspace/slides/api/reference/mcp/tools_list/read_presentation.md.txt) | Retrieves a JSON representation of a Slides presentation. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`read_slide_page`](https://developers.google.com/workspace/slides/api/reference/mcp/tools_list/read_slide_page.md.txt) | Retrieves a JSON representation of a single slide page from a presentation. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`read_slide_page_thumbnail`](https://developers.google.com/workspace/slides/api/reference/mcp/tools_list/read_slide_page_thumbnail.md.txt) | Retrieves the thumbnail image URL and dimensions for a single slide page. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`update_presentation`](https://developers.google.com/workspace/slides/api/reference/mcp/tools_list/update_presentation.md.txt) | Applies a set of `batchUpdate` requests to edit a presentation. | Write | `/mcp/v1`, `/mcp/v1self` |

## Calendar toolsets

The Calendar MCP server lets AI agents list calendars and
events, search events, suggest free meeting times, and create, update, respond
to, or delete events. For setup instructions and full schemas, see
[Configure the Calendar MCP server](https://developers.google.com/workspace/calendar/api/guides/configure-mcp-server.md.txt) and the
[Calendar MCP reference](https://developers.google.com/workspace/calendar/api/v3/reference/mcp.md.txt).

The Calendar MCP server provides the following toolset
endpoints:

- Primary endpoint: `https://calendarmcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://calendarmcp.googleapis.com/mcp/v1self`

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`create_event`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/create_event.md.txt) | Creates a new event on a specified calendar. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`delete_event`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/delete_event.md.txt) | Deletes an event from a specified calendar. | Write | `/mcp/v1` only |
| [`get_event`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/get_event.md.txt) | Retrieves details for a single event on a specified calendar. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_calendars`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/list_calendars.md.txt) | Lists calendars that the user owns or subscribes to, returning each calendar's ID. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_events`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/list_events.md.txt) | Lists events on a specified calendar matching the provided constraints. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`respond_to_event`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/respond_to_event.md.txt) | Responds to an invitation for an event on a calendar. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`search_events`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/search_events.md.txt) | Searches events on the user's primary calendar using semantic search. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`suggest_time`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/suggest_time.md.txt) | Suggests available meeting time periods across one or more calendars. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`update_event`](https://developers.google.com/workspace/calendar/api/v3/reference/mcp/tools_list/update_event.md.txt) | Updates an existing event on a specified calendar. | Write | `/mcp/v1`, `/mcp/v1self` |

## Chat toolsets

The Chat MCP server lets AI agents search conversations and
messages, list messages and memberships, send messages, update read states, and
manage notification preferences. For setup instructions and full schemas, see
[Configure the Chat MCP server](https://developers.google.com/workspace/chat/api/guides/configure-mcp-server.md.txt) and the
[Chat MCP reference](https://developers.google.com/workspace/chat/api/reference/mcp.md.txt).

The Chat MCP server provides the following toolset endpoints:

- Primary endpoint: `https://chatmcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://chatmcp.googleapis.com/mcp/v1self`

> [!NOTE]
> **Note:** Write operations such as `send_message` require a configured Google Chat app in your Google Cloud project. Using the `participants` filter with `search_conversations` requires a `chat.memberships` scope in addition to a `chat.spaces` scope.

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`get_notification_settings`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/get_notification_settings.md.txt) | Retrieves notification preferences, mute state, or thread follow state for a conversation. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_memberships`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/list_memberships.md.txt) | Lists members in a Chat conversation. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_messages`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/list_messages.md.txt) | Retrieves messages from a Chat space, direct message, or group chat in Markdown format. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`mark_as_read`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/mark_as_read.md.txt) | Marks Chat conversations and threads as read for the calling user. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`mark_as_unread`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/mark_as_unread.md.txt) | Marks a Chat conversation or thread as unread for the calling user. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`search_conversations`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/search_conversations.md.txt) | Searches for spaces by display name, or direct messages and group chats by participant email addresses. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`search_messages`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/search_messages.md.txt) | Searches for Chat messages across accessible spaces or within a specific conversation in Markdown format. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`send_message`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/send_message.md.txt) | Sends a Chat message with Markdown formatting and optional citations. | Write | `/mcp/v1` only |
| [`update_notification_settings`](https://developers.google.com/workspace/chat/api/reference/mcp/tools_list/update_notification_settings.md.txt) | Updates space notification preferences, mute state, or thread follow state for a conversation. | Write | `/mcp/v1`, `/mcp/v1self` |

## Tasks toolsets

The Tasks MCP server lets AI agents list task lists and tasks,
retrieve task details, create and update tasks, mark tasks complete or
incomplete, and delete or restore tasks. For setup instructions and full
schemas, see [Configure the Tasks MCP server](https://developers.google.com/workspace/tasks/guides/configure-mcp-server.md.txt) and
the [Tasks MCP reference](https://developers.google.com/workspace/tasks/reference/mcp).

The Tasks MCP server provides the following toolset endpoints:

- Primary endpoint: `https://tasksmcp.googleapis.com/mcp/v1`
- Self-mode endpoint: `https://tasksmcp.googleapis.com/mcp/v1self`

> [!NOTE]
> **Note:** To use the Tasks MCP server, enable `tasksmcp.googleapis.com` in your Google Cloud project. You don't need to enable the Google Tasks API separately.

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`complete_task`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/complete_task) | Marks a task as complete. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`create_task`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/create_task) | Creates a new task or scheduled reminder in a task list. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`delete_task`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/delete_task) | Deletes an existing task. Non-shared tasks can be restored with `undelete_task`. | Write | `/mcp/v1` only |
| [`get_task`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/get_task) | Retrieves a single task by ID, including completed and deleted tasks. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_task_lists`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/list_task_lists) | Lists the authenticated user's task lists. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`list_tasks`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/list_tasks.md.txt) | Lists tasks across one or all task lists, returning uncompleted tasks by default. | Read-only | `/mcp/v1`, `/mcp/v1self` |
| [`uncomplete_task`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/uncomplete_task) | Marks a completed task as incomplete. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`undelete_task`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/undelete_task) | Restores a deleted non-shared task. | Write | `/mcp/v1`, `/mcp/v1self` |
| [`update_task`](https://developers.google.com/workspace/tasks/reference/mcp/tools_list/update_task) | Updates an existing task's details. Use `complete_task` or `uncomplete_task` to change completion state. | Write | `/mcp/v1`, `/mcp/v1self` |

## People API toolset

The People API MCP server lets AI agents retrieve the user's profile
information and search personal contacts or the organization's directory. For
setup instructions and full schemas, see
[Configure the People API MCP server](https://developers.google.com/people/v1/configure-mcp-server.md.txt) and the
[People API MCP reference](https://developers.google.com/people/api/mcp.md.txt).

The People API MCP server provides the following toolset endpoint:

- Primary endpoint: `https://people.googleapis.com/mcp/v1`

| Tool | Description | Access | Toolsets |
|---|---|---|---|
| [`get_user_profile`](https://developers.google.com/people/api/mcp/tools_list/get_user_profile.md.txt) | Retrieves the authenticated user's profile name and email address. | Read-only | `/mcp/v1` only |
| [`search_contacts`](https://developers.google.com/people/api/mcp/tools_list/search_contacts.md.txt) | Searches the authenticated user's personal contacts. | Read-only | `/mcp/v1` only |
| [`search_directory_people`](https://developers.google.com/people/api/mcp/tools_list/search_directory_people.md.txt) | Searches the organization's Google Workspace directory. Requires a Google Workspace account. | Read-only | `/mcp/v1` only |

## Get live tool specifications

To fetch the current tool list and full JSON input and output schemas directly
from any Google Workspace MCP server, send a `tools/list` request to
the server's `/mcp/v1` or `/mcp/v1self` endpoint:

```bash
curl --location \
  'https://SERVER_HOST/mcp/v1' \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json, text/event-stream' \
  --data '{
    "method": "tools/list",
    "jsonrpc": "2.0",
    "id": 1
  }'
```

Replace the following:

- `SERVER_HOST`: The hostname of the target Google Workspace MCP server, such as `gmailmcp.googleapis.com`.
- `ACCESS_TOKEN`: A valid OAuth 2.0 access token.

## Related topics

- [Configure Google Workspace MCP servers](https://developers.google.com/workspace/guides/configure-mcp-servers.md.txt)
- [Configure security for Google Workspace MCP servers](https://developers.google.com/workspace/guides/configure-mcp-security.md.txt)
- [Handle user approvals with form elicitation](https://developers.google.com/workspace/guides/mcp-elicitation.md.txt)
- [Use the Google Workspace command-line interface
  (CLI)](https://developers.google.com/workspace/guides/workspace-cli)
- [Configure the Universal Search MCP server](https://developers.google.com/workspace/guides/universal-search-mcp.md.txt) [( Developer Preview)](https://developers.google.com/workspace/preview.md.txt)