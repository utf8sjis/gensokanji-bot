import io, json

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import client
from apiclient.http import MediaFileUpload

import config


SCOPES = ['https://www.googleapis.com/auth/drive']
DIR_PATH = '/tmp/'
TMP_FILE_NAME = 'tweeted_id_list.json'
FOLDER_ID = '1umeEgiccFzr3rd7OwkiFXVBQ8gpqcExY'  # .apiフォルダ


def access_drive():
    creds = client.Credentials.new_from_json(config.GOOGLE_API_ACCESS_TOKEN)
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))

    return drive_service


def get_tweeted_id_list():
    # ダウンロード
    drive_service = access_drive()

    results = drive_service.files().list(
        pageSize=10,
        fields='nextPageToken, files(id, name)',
        q="'{}' in parents".format(FOLDER_ID)).execute()
    items = results.get('files', [])

    if not items:
        tweeted_id_list = []
    else:
        for item in items:
            if TMP_FILE_NAME == item['name']:
                request = drive_service.files().get_media(fileId=item['id'])
                fh = io.FileIO(DIR_PATH + TMP_FILE_NAME, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

        # 読み込み
        with open(DIR_PATH + TMP_FILE_NAME, 'r') as f:
            tweeted_id_list = json.load(f)

    return tweeted_id_list


def upload_tweeted_id_list(tweeted_id_list):
    # 書き込み
    with open(DIR_PATH + TMP_FILE_NAME, 'w') as f:
        f.write(json.dumps(tweeted_id_list))

    # アップロード
    drive_service = access_drive()

    media_body = MediaFileUpload(
        DIR_PATH + TMP_FILE_NAME,
        mimetype='application/octet-stream',
        resumable=True)

    query = "name = '{}' and '{}' in parents and trashed=false".format(
        TMP_FILE_NAME, FOLDER_ID)
    res = drive_service.files().list(q=query).execute()

    if not res['files']:
        drive_service.files().create(
            body={'name': TMP_FILE_NAME,
                'mimeType': 'application/octet-stream',
                'parents':[FOLDER_ID]},
            media_body=media_body,
        ).execute()
    else:
        drive_service.files().update(
            fileId=res['files'][0]['id'],
            media_body=media_body).execute()
