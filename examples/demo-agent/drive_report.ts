// DEMO DATA: a made-up report writer that files a summary in Drive and shares it.
import { google } from "googleapis";

export async function fileReport(auth: any, title: string, folderId: string, teamEmail: string) {
  const drive = google.drive({ version: "v3", auth });
  const sheets = google.sheets({ version: "v4", auth });
  const file = await drive.files.create({
    requestBody: { name: title, mimeType: "application/vnd.google-apps.document" },
  });
  await drive.files.update({ fileId: file.data.id!, addParents: folderId });
  await drive.permissions.create({
    fileId: file.data.id!,
    requestBody: { role: "reader", type: "user", emailAddress: teamEmail },
  });
  await sheets.spreadsheets.values.append({
    spreadsheetId: "LOG_SHEET_ID",
    range: "Log!A:C",
    valueInputOption: "RAW",
    requestBody: { values: [[title, file.data.id, new Date().toISOString()]] },
  });
}
