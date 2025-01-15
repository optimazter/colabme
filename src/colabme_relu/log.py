import click
from enum import Enum



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

    def set_verbose(value: bool):
        Logger.__verbose = value
        Logger.echo("Verbose mode enabled.")

    def echo(message, log_level: LogLevel = LogLevel.INFO):
        if Logger.__verbose or log_level != LogLevel.INFO:
            click.echo(f"[{log_level_to_str(log_level)}]: {message}")