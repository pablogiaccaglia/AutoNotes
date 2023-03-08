from __future__ import print_function

import os
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from enum import Enum
from apiclient import errors
import requests
from urllib.parse import unquote
class MIMETYPE(Enum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    PDF = "application/pdf"

SCOPES = ['https://www.googleapis.com/auth/drive']

class GDrive:
    """

    """
    def __init__(self, credentials_path, permission_id, SCOPES = None):
        if SCOPES is None:
            SCOPES = ['https://www.googleapis.com/auth/drive']

        self.permission_id = permission_id
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('../configs/token.json'):
            creds = Credentials.from_authorized_user_file('../configs/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES)
                creds = flow.run_local_server(port = 0)
            # Save the credentials for the next run
            with open('../configs/token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('drive', 'v3', credentials = creds)
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f'An error occurred: {error}')

    def create_folder(self, folder_name):
        """ Create a folder and prints the folder ID
        Returns : Folder Id

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """

        try:

            folder_id = self.get_folder_id(folder_name = folder_name)

            if folder_id:
                return folder_id

            file_metadata = {
                'name':     folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }



            # pylint: disable=maybe-no-member
            file = self.service.files().create(body = file_metadata, fields = 'id'
                                               ).execute()
            # print(F'Folder ID: "{file.get("id")}".')
            return file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None

    def get_folder_id(self, folder_name):

        try:

            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = self.service.files().list(q = "mimeType='application/vnd.google-apps.folder'",
                                                     spaces = 'drive',
                                                     fields = 'nextPageToken, '
                                                              'files(id, name)',
                                                     pageToken = page_token).execute()
                for file in response.get('files', []):
                    if file.get("name") == folder_name:
                        # print(F'Found file: {file.get("name")}, {file.get("id")}')
                        return file.get("id")
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

            return None

        except HttpError as error:
            print(F'An error occurred: {error}')
            files = None

        return files

    def upload_file(self, folder_name, file_path, file_name, mime_type, folder_id = None, create_folder_if_missing=True):
        try:

            if not folder_id:
                folder_id = self.get_folder_id(folder_name = folder_name)

                if not folder_id:
                    if create_folder_if_missing:
                        folder_id = self.create_folder(folder_name = folder_name)
                    else:
                        print("Missing folder")
                        return

            file_metadata = {
                'name':    file_name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path,
                                    mimetype = mime_type , resumable = True)
            # pylint: disable=maybe-no-member
            file = self.service.files().create(body = file_metadata, media_body = media,
                                               fields = 'id').execute()
            print(F'File ID: "{file.get("id")}".')
            return file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None

    def __get_web_view_link_file_id(self, url):
        return url.split("/")[-2]

    def __get_link_from_file_id(self, id, unquote_ = False):

        url = f"https://drive.google.com/uc?id={id}"
        if unquote_:
                url = unquote(url, encoding="utf-8")

        return url

    def upload_file_and_get_url(self, folder_name,
                                file_path,
                                file_name,
                                mime_type,
                                folder_id = None,
                                create_folder_if_missing=True,
                                new_role = None):

        file_id = self.upload_file(folder_name = folder_name, file_path = file_path, file_name = file_name, mime_type = mime_type, folder_id = folder_id,
                         create_folder_if_missing = create_folder_if_missing)

        if new_role:
            permission = {
                'type_': 'anyone',
                'role': new_role,
            }
            self.create_permission(file_id = file_id, permission_body = permission)

        url = self.get_file(file_id = file_id, fields = "webViewLink")['webViewLink']
        url = self.__get_link_from_file_id(id = self.__get_web_view_link_file_id(url = url), unquote_ = True)
        print(url)
        return url
        #r = requests.get(url)
        #print(r.url)
        #return r.url

    def upload_multiple_files_same_folder(self,
                                          folder_name,
                                          file_paths,
                                          file_names,
                                          mime_types,
                                          create_folder_if_missing=True):
        assert len(file_paths) == len(file_names) and len(file_names) == len(mime_types)

        folder_id = self.get_folder_id(folder_name = folder_name)

        if not folder_id:
            if create_folder_if_missing:
                folder_id = self.create_folder(folder_name = folder_name)
            else:
                print("Missing folder")
                return

        for idx in range(len(file_paths)):
            self.upload_file(folder_name = folder_name,
                             file_path = file_paths[idx],
                             file_name = file_names[idx],
                             folder_id = folder_id,
                             mime_type = mime_types[idx])

    def update_permission(self, file_id, new_role):
        """Update a permission's role.

        Args:
          service: Drive API service instance.
          file_id: ID of the file to update permission for.
          permission_id: ID of the permission to update.
          new_role: The value 'owner', 'writer' or 'reader'.

        Returns:
          The updated permission if successful, None otherwise.
        """
        try:
            # First retrieve the permission from the API.
            permission = self.service.permissions().get(
                    fileId = file_id, permissionId = self.permission_id).execute()

            print(permission)
            permission['role'] = new_role
            return self.service.permissions().update(
                    fileId = file_id, permissionId = self.permission_id, body = permission).execute()
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
        return None

    def create_permission(self, file_id, permission_body):
        return self.service.permissions().create(fileId = file_id, body = permission_body).execute()

    def get_file(self, file_id, fields = None):
        return self.service.files().get(fileId = file_id, fields = fields).execute()

if __name__ == '__main__':
    SCOPES = ['https://www.googleapis.com/auth/drive']
    folder_name= 'Notion-NLP-Media'
    file_path = "Page_1.jpg"
    gdrive = GDrive(credentials_path = '../configs/credentials.json', SCOPES = SCOPES)
    #gdrive.create_folder(folder_name =  folder_name)
    #gdrive.upload_file(folder_name = folder_name,
    # file_path = file_path, file_name = file_path, mime_type = MIMETYPE.JPEG.value)
    gdrive.upload_multiple_files_same_folder(folder_name = folder_name,
                                             file_paths = [file_path],
                                             file_names = [file_path],
                                             mime_types = [MIMETYPE.JPEG.value])