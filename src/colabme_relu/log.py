import click
from enum import Enum
from rich.progress import Progress


class LogLevel(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3

def log_level_to_str(log_level: LogLevel):
    match log_level:
        case LogLevel.INFO:
            return "INFO"
        case LogLevel.WARNING:
            return "WARNING"
        case LogLevel.ERROR:
            return "ERROR"

class Logger:

    __verbose = False
    __task = None
    __progress = None

    def set_task(task, progress: Progress):
        Logger.__task = task
        Logger.__progress = progress
    
    def remove_task():
        Logger.__task = None
        Logger.__progress = None

    def set_verbose(value: bool):
        Logger.__verbose = value
        Logger.echo("Verbose mode enabled.")

    def echo(message, log_level: LogLevel = LogLevel.INFO):
        if Logger.__task is not None:
            Logger.__progress.update(Logger.__task, description=message)
            Logger.__progress.refresh()
        elif Logger.__verbose or log_level != LogLevel.INFO:
            click.echo(f"[{log_level_to_str(log_level)}]: {message}")