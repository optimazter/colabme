import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from rich.progress import Progress

from colabme_relu.tracker import Tracker
from colabme_relu.log import Logger, LogLevel




def upload(service, tracker: Tracker, paths: list = None, parent_id: str = None):
    with Progress() as progress:
        task = progress.add_task("Uploading files", total=len(paths))

        for path in paths:
            id = None

            if path in tracker.files.keys():
                Logger.echo(f"{path} is already tracked. Deleting it from Google Drive to update it.")
                delete_path(service, tracker.files[path])

            if os.path.isfile(path):
                id = upload_file(service, path, parent_id)

            elif os.path.isdir(path):
                id = upload_directory(service, path, parent_id)

            else:
                Logger.echo(f"{path} is not a directory or file!", LogLevel.WARNING)

            if id:
                tracker.files[path] = id
            
            progress.update(task, advance=1)
            progress.refresh()




def load_tracker(tracker_file: os.path) -> Tracker:
    if not os.path.isfile(tracker_file):
        tracker = Tracker()
        Logger.echo(f"Tracker file not found. Creating a new one at: {tracker_file}.")
    else:
        with open(tracker_file, "r") as f:
            tracker = Tracker.from_json(json.load(f))
        Logger.echo(f"Loaded tracker from: {tracker_file}.")
    return tracker



def save_tracker(tracker_file: os.path, tracker: Tracker):
    with open(tracker_file, "w") as f:
        json.dump(tracker.to_json(), f)



def create_service(service_account_file: str, scopes: list):
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    return build("drive", "v3", credentials=credentials)




def upload_directory(service, directory, parent_id, first_id = None):
    id = create_folder(service, directory, parent_id)
    if first_id is None:
        first_id = id
    for name in os.listdir(directory):
        name = os.path.join(directory, name)
        if os.path.isfile(name):
            upload_file(service, name, id)
        else:
            upload_directory(service, name, id)
    return first_id
    


def create_folder(service, folder_name, parent = None):
    try:
        folder_metadata = {
            'name': os.path.basename(folder_name),
            "mimeType": "application/vnd.google-apps.folder",
            'parents': [parent] if parent else [] 
        }
        created_folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        Logger.echo(f'Created folder {folder_name} with ID: {created_folder["id"]}')
        return created_folder["id"]
    except Exception as e:
        Logger.echo(f"Error creating folder: {folder_name}")
        Logger.echo(f"Error details: {str(e)}")
        return None


def upload_file(service, file_path, parent_id):
    try:
        media = MediaFileUpload(file_path, resumable=True)
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [parent_id]
        }
        created_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        Logger.echo(f'Uploaded file: {file_path} with ID: {created_file["id"]}.')
        return created_file["id"]
    except Exception as e:
        Logger.echo(f"Error uploading file: {file_path}")
        Logger.echo(f"Error details: {str(e)}")
        return None


def delete_path(service, folder_id):
    try:
        service.files().delete(fileId=folder_id).execute()
        Logger.echo(f"Successfully deleted file/folder with ID: {folder_id}")
    except Exception as e:
        Logger.echo(f"Error deleting file/folder with ID: {folder_id}")
        Logger.echo(f"Error details: {str(e)}")





