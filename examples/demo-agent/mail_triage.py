# DEMO DATA: a made-up email triage agent that calls the Gmail and Calendar REST APIs.
import base64

from googleapiclient.discovery import build


def triage(creds, llm):
    gmail = build("gmail", "v1", credentials=creds)
    threads = gmail.users().threads().list(userId="me", q="is:unread").execute()
    for t in threads.get("threads", []):
        thread = gmail.users().threads().get(userId="me", id=t["id"]).execute()
        label = llm.classify(thread)
        gmail.users().threads().modify(
            userId="me", id=t["id"], body={"addLabelIds": [label], "removeLabelIds": ["UNREAD"]}
        ).execute()
        for msg in thread["messages"]:
            for part in msg["payload"].get("parts", []):
                if part.get("filename"):
                    att = (
                        gmail.users()
                        .messages()
                        .attachments()
                        .get(userId="me", messageId=msg["id"], id=part["body"]["attachmentId"])
                        .execute()
                    )
                    llm.read(base64.urlsafe_b64decode(att["data"]))


def reply(creds, raw):
    gmail = build("gmail", "v1", credentials=creds)
    draft = gmail.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    gmail.users().drafts().send(userId="me", body={"id": draft["id"]}).execute()


def book_followup(creds, event):
    cal = build("calendar", "v3", credentials=creds)
    cal.events().insert(calendarId="primary", body=event).execute()
    cal.calendarList().list().execute()
