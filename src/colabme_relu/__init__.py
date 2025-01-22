import os
import sys
import click

from colabme_relu.google_utils import upload_paths, update_paths, remove_paths, remove_all_paths, load_tracker, save_tracker, load_service
from colabme_relu.log import Logger, LogLevel



SCOPES = ["https://www.googleapis.com/auth/drive"]
DIR = os.path.join(os.getcwd(), ".colabme")
TRACKER_FILE = os.path.join(DIR, "colabme.json")



@click.group()
def cli():
    pass

@cli.command()
@click.option("-s", "--service", help="Google service account file to use.", default=None)
@click.option("-p", "--parent", help="Parent ID of the folder to upload the files.", default=None)
@click.option("-v", "--verbose", help="Verbose mode", is_flag=True, default=False)
def setup(service, parent, verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        Logger.echo(f"Creating .colabme directory. in the current working directory: {DIR}.")
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)

    if service:
        tracker.service_account_file = service
        Logger.echo(f"Service account file set to: {service}.")

    if parent:
        tracker.parent_id = parent
        Logger.echo(f"Parent ID set to: {parent}.")

    save_tracker(TRACKER_FILE, tracker)


@cli.command()
@click.argument("files", nargs=-1)
@click.option("-u", "--update", help="Update all tracked files.", is_flag=True, default=False)
@click.option("-a", "--all", help="Commit all files in current directory.", is_flag=True, default=False)
@click.option("-v", "--verbose", help="Verbose mode", is_flag=True, default=False)
def commit(files: tuple[str, ...], update, all, verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)
    service = load_service(tracker, SCOPES)

    if not service:
        sys.exit(1)
    
    if update:
        Logger.echo("Updating all tracked files.")
        update_paths(service, tracker)
    
    if files:
        Logger.echo("Uploading specified files.")
        upload_paths(service, tracker, files, tracker.parent_id)
    
    if all:
        Logger.echo("Uploading all files in the current directory.")
        upload_paths(service, tracker, os.listdir("."), tracker.parent_id)

    save_tracker(TRACKER_FILE, tracker)
    Logger.echo("The operation completed.")

@cli.command()
@click.argument("files", nargs=-1)
@click.option("-a", "--all", help="Remove all files in the repository!", is_flag=True, default=False)
@click.option("-v", "--verbose", help="Verbose mode", is_flag=True, default=False)
def remove(files: tuple[str, ...], all, verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)
    service = load_service(tracker, SCOPES)

    if not service:
        sys.exit(1)

    if files:
        Logger.echo(f"Removing specified files: {files}.")
        remove_paths(service, tracker, files)
    
    if all:
        Logger.echo("Removing all tracked files.")
        remove_all_paths(service, tracker)

    save_tracker(TRACKER_FILE, tracker)
    Logger.echo("The operation completed.")

@cli.command()
@click.argument("files", nargs=-1)
@click.option("-v", "--verbose", help="Verbose mode", is_flag=True, default=False)
def ignore(files: tuple[str, ...], verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)

    if files:
        Logger.echo(f"Ignoring specified files: {files}.")
        tracker.ignore_files(files)

    save_tracker(TRACKER_FILE, tracker)
    Logger.echo("The operation completed.")



@cli.command()
@click.argument("files", nargs=-1)
@click.option("-a", "--all", help="Unignore all files.", is_flag=True, default=False)
@click.option("-v", "--verbose", help="Verbose mode", is_flag=True, default=False)
def unignore(files: tuple[str, ...], all, verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)

    if files:
        Logger.echo(f"Unignoring specified files: {files}.")
        tracker.unignore_files(files)
    
    if all:
        Logger.echo("Unignoring all files.")
        tracker.ignored_files = []

    save_tracker(TRACKER_FILE, tracker)
    Logger.echo("The operation completed.")


@cli.command()
def list():
    Logger.set_verbose(True)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)

    if not tracker.files:
        Logger.echo("No files are tracked.")
    else:
        Logger.echo("Tracked files:")
        for file in tracker.files:
            Logger.echo(f"{file.path}: {file.id}")

    if tracker.ignored_files:
        Logger.echo("Ignored files:")
        for file in tracker.ignored_files:
            Logger.echo(file)
    