#!/bin/sh
# DEMO DATA: a made-up shell hook an agent runs to fetch new mail and delete spam.
TOKEN="$(cat token.txt)"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/history?startHistoryId=$1"
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/$2"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=10"
