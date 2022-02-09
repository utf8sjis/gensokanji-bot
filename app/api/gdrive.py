import io

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import client
from apiclient.http import MediaFileUpload

import config


FOLDER_ID = '1umeEgiccFzr3rd7OwkiFXVBQ8gpqcExY'  # gensokanji-botフォルダ


# 認証
def access_drive():
    creds = client.Credentials.new_from_json(config.GOOGLE_API_ACCESS_TOKEN)
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))

    return drive_service


# ファイルをダウンロード
def download_file(to_dir_name, file_name):
    drive_service = access_drive()

    results = drive_service.files().list(
        pageSize=10,
        fields='nextPageToken, files(id, name)',
        q="'{}' in parents".format(FOLDER_ID)).execute()
    items = results.get('files', [])

    if not items:
        return False
    else:
        for item in items:
            if file_name == item['name']:
                request = drive_service.files().get_media(fileId=item['id'])
                fh = io.FileIO(to_dir_name + file_name, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
        return True


# ファイルを更新
def upload_file(from_dir_name, file_name):
    drive_service = access_drive()

    media_body = MediaFileUpload(
        from_dir_name + file_name,
        mimetype='application/octet-stream',
        resumable=True)

    query = "name = '{}' and '{}' in parents and trashed=false".format(
        file_name, FOLDER_ID)
    res = drive_service.files().list(q=query).execute()

    if not res['files']:
        drive_service.files().create(
            body={'name': file_name,
                'mimeType': 'application/octet-stream',
                'parents':[FOLDER_ID]},
            media_body=media_body,
        ).execute()
    else:
        drive_service.files().update(
            fileId=res['files'][0]['id'],
            media_body=media_body).execute()
