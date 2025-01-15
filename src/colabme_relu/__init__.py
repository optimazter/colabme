import os
import sys
import click

from colabme_relu.google_utils import upload, load_tracker, save_tracker, create_service
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
def commit(files: tuple[str, ...], update, verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)


    tracker = load_tracker(TRACKER_FILE)

    if tracker.service_account_file is None:
        Logger.echo("No service account file provided. Please run colab setup to provide a service account file.", LogLevel.ERROR)
        sys.exit(1)

    elif not os.path.isfile(tracker.service_account_file):
        Logger.echo(f"Specified service account file {tracker.service_account_file} does not exist.", LogLevel.ERROR)
        sys.exit(1)

    else:
        service = create_service(tracker.service_account_file, SCOPES)   
        Logger.echo(f"Loading service from file:  {tracker.service_account_file}.")
    
    if update:
        Logger.echo("Updating all tracked files.")
        upload(service, tracker, tracker.files, tracker.parent_id)
    
    if files:
        Logger.echo("Uploading specified files.")
        upload(service, tracker, files, tracker.parent_id)
    
    if all:
        Logger.echo("Uploading all files in the current directory.")
        upload(service, tracker, os.listdir("."), tracker.parent_id)

    save_tracker(TRACKER_FILE, tracker)
    Logger.echo("The operation completed.")



@click.command()
@click.argument("files", nargs=-1)
@click.option("-v", "--verbose", help="Verbose mode", is_flag=True, default=False)
def ignore(files: tuple[str, ...], verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)

    if files:
        Logger.echo(f"Ignoring specified files: {files}.")
        tracker.ignored_files.extend(files)

    save_tracker(TRACKER_FILE, tracker)
    Logger.echo("The operation completed.")



@click.command()
@click.argument("files", nargs=-1)
@click.option("-a", "--all", help="Unignore all files.", is_flag=True, default=False)
@click.option("-v", "--verbose", help="Verbose mode", is_flag=True, default=False)
def unignore(files: tuple[str, ...], verbose):
    Logger.set_verbose(verbose)

    if not os.path.isdir(DIR):
        os.mkdir(DIR)

    tracker = load_tracker(TRACKER_FILE)

    if files:
        Logger.echo(f"Unignoring specified files: {files}.")
        tracker.ignored_files = [file for file in tracker.ignored_files if file not in files]
    
    if all:
        Logger.echo("Unignoring all files.")
        tracker.ignored_files = []

    save_tracker(TRACKER_FILE, tracker)
    Logger.echo("The operation completed.")