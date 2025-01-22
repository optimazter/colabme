import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from rich.progress import Progress
import datetime as dt

from colabme_relu.tracker import Tracker, File
from colabme_relu.log import Logger, LogLevel

def upload_paths(service, tracker: Tracker, paths: list, parent_id: str = None):
    with Progress() as progress:
        _upload_paths(progress, service, tracker, paths, parent_id)

def update_paths(service, tracker: Tracker):
    with Progress() as progress:
        _update_paths(progress, service, tracker)

def remove_paths(service, tracker: Tracker, paths: list):
    with Progress() as progress:
        _remove_paths(progress, service, tracker, paths)

def remove_all_paths(service, tracker: Tracker):
    with Progress() as progress:
        _remove_all_paths(progress, service, tracker)



def _upload_paths(progress, service, tracker: Tracker, paths: list, parent_id: str = None):
    
        task = progress.add_task(f"Uploading files in parent directory {parent_id}", total=len(paths))
        Logger.set_task(task, progress)

        for path in paths:

            if not os.path.exists(path):
                Logger.echo(f"{path} does not exist!", LogLevel.WARNING)
                progress.update(task, advance=1)
                progress.refresh()
                continue

            file: File = tracker.get_file_by_path(path)
            if file is None:
                file = File(path)
            file.parent_id = parent_id

            def update():
                file.date = os.path.getmtime(file.path)
                tracker.add_file(file)
                progress.update(task, advance=1)
                progress.refresh()
            
            if tracker.is_ignored(file.path):
                Logger.echo(f"{file.path} is ignored. Skipping.")

            elif file.is_file():
                if not tracker.is_ignored(file.path) and (not file.is_uploaded() or file.is_updated()):
                    if file.is_uploaded():
                        Logger.echo(f"{path} is already tracked. Deleting it from Google Drive to update it.")
                        delete_path(service, file.id)
                    if file.is_updated():
                        Logger.echo(f"{path} is updated {dt.datetime.fromtimestamp(file.date)}. Updating it in Google Drive.")
                    Logger.echo(f"Uploading {file.path}.")
                    file.id = upload_file(service, file.path, file.parent_id)
                    update()

            elif file.is_dir():
                if not file.is_uploaded():
                    Logger.echo(f"{file.path} is an unuploaded directory. Creating it in Google Drive.")
                    file.id = create_folder(service, file.path, file.parent_id)
                    update()
                _upload_paths(progress, service, tracker, [os.path.join(file.path, f) for f in os.listdir(file.path)], file.id)

            else:
                Logger.echo(f"{file.path} is not a valid directory or file!", LogLevel.WARNING)

        Logger.remove_task()


def _update_paths(progress, service, tracker: Tracker):

    task = progress.add_task("Updating files", total=len(tracker.files))
    Logger.set_task(task, progress)

    file: File
    for file in tracker.files:
        if file.is_uploaded() and file.is_updated():
            Logger.echo(f"{file.path} is updated. Updating it in Google Drive.")
            delete_path(service, file.id)
            file.id = upload_file(service, file.path, file.parent_id)

        progress.update(task, advance=1)
        progress.refresh()

    Logger.remove_task()




def _remove_paths(progress, service, tracker: Tracker, paths: list):
    task = progress.add_task("Removing files", total=len(paths))

    Logger.set_task(task, progress)

    for path in paths:
        if tracker.is_tracked(path):
            file: File = tracker.get_file_by_path(path)
            Logger.echo(f"Removing {path} from Google Drive.")
            if file.is_uploaded():
                delete_path(service, file.id)
                tracker.remove_file_by_path(path)
                if file.is_dir():
                    tracker.remove_parent(file.id)
            else:
                Logger.echo(f"{path} is not a directory or file!", LogLevel.WARNING)


        progress.update(task, advance=1)
        progress.refresh()

    Logger.remove_task()


def _remove_all_paths(progress, service, tracker: Tracker):
    _remove_paths(progress, service, tracker, [file.path for file in tracker.files])


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
        Logger.echo(f"Error creating folder: {folder_name}", LogLevel.ERROR)
        Logger.echo(f"Error details: {str(e)}", LogLevel.ERROR)
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
        Logger.echo(f"Error uploading file: {file_path}", LogLevel.ERROR)
        Logger.echo(f"Error details: {str(e)}", LogLevel.ERROR)
        return None


def delete_path(service, folder_id):
    try:
        service.files().delete(fileId=folder_id).execute()
        Logger.echo(f"Successfully deleted file/folder with ID: {folder_id}")
    except Exception as e:
        Logger.echo(f"Error deleting file/folder with ID: {folder_id}", LogLevel.ERROR)
        Logger.echo(f"Error details: {str(e)}", LogLevel.ERROR)




def load_service(tracker: Tracker, scopes: list):
    if tracker.service_account_file is None:
        Logger.echo("No service account file provided. Please run colab setup to provide a service account file.", LogLevel.ERROR)
        return None

    elif tracker.parent_id is None:
        Logger.echo("No parent ID provided. Please run colab setup to provide a parent ID.", LogLevel.ERROR)
        return None

    elif not os.path.isfile(tracker.service_account_file):
        Logger.echo(f"Specified service account file {tracker.service_account_file} does not exist.", LogLevel.ERROR)
        return None

    else:
        service = create_service(tracker.service_account_file, scopes)   
        Logger.echo(f"Loading service from file:  {tracker.service_account_file}.")
        return service
    

