import datetime as dt
import os

class Field:
    FILES = "files"
    IGNORED_FILES = "ignored_files"
    SERVICE_ACCOUNT_FILE = "service_account_file"
    PARENT_ID = "parent_id"


class File:

    def __init__(self, path: str, date: float = None, id: str = None, parent_id: str = None):
        self.path = os.path.abspath(path)
        self.id = id
        self.date = date
        self.parent_id = parent_id

    def is_dir(self):
        return os.path.isdir(self.path)
    
    def is_file(self):
        return os.path.isfile(self.path)
    
    def is_uploaded(self):
        return self.id is not None
    

    def is_updated(self):
        if self.date is None:
            return False
        return os.path.getmtime(self.path) > self.date

    def to_json(self):
        return {
            "path" : self.path,
            "id" : self.id,
            "date": self.date,
            "parent_id": self.parent_id
        }
    
    def from_json(json):
        return File(
            path = json["path"],
            id = json["id"],
            date = float(json["date"]),
            parent_id = json["parent_id"]
        )

class Tracker:

    def __init__(self, files: list = [], ignored_files: list = [], service_account_file: str = None, parent_id: str = None):
        self.files = files
        self.ignored_files = ignored_files
        self.service_account_file = service_account_file
        self.parent_id = parent_id
    

    def add_file(self, file: File):
        if self.get_file_by_path(file.path) is not None:
            self.remove_file_by_path(file.path)
        self.files.append(file)
    
    
    def get_file_by_path(self, path: str):
        for file in self.files:
            if os.path.abspath(file.path) == os.path.abspath(path):
                return file
        return None

    def remove_file(self, file: File):
        self.files.remove(file)
    
    def remove_file_by_path(self, path: str):
        self.files = [file for file in self.files if os.path.abspath(file.path) != os.path.abspath(path)]

    def remove_parent(self, parent_id: str):
        self.files = [file for file in self.files if parent_id != file.parent_id]
    
    def ignore_file(self, path: str):
        self.ignored_files.append(os.path.abspath(path))

    def ignore_files(self, paths: list):
        self.ignored_files += [os.path.abspath(path) for path in paths]
    
    def unignore_file(self, path: str):
        self.ignored_files = [file for file in self.ignored_files if os.path.abspath(file.path) != os.path.abspath(path)]
    
    def unignore_files(self, paths: list):
        paths = [os.path.abspath(path) for path in paths]
        self.ignored_files = [file for file in self.ignored_files if file not in paths]

    def is_ignored(self, path):
        for ignored in self.ignored_files:
            if os.path.abspath(ignored) == os.path.abspath(path):
                return True
        return False

    def is_tracked(self, path):
        for file in self.files:
            if os.path.abspath(file.path) == os.path.abspath(path):
                return True
        return False
    

    def from_json(json):
        return Tracker(
            files = [File.from_json(file) for file in json[Field.FILES]],
            ignored_files= json[Field.IGNORED_FILES] if Field.IGNORED_FILES in json else [],
            service_account_file= json[Field.SERVICE_ACCOUNT_FILE] if Field.SERVICE_ACCOUNT_FILE in json else None,
            parent_id = json[Field.PARENT_ID] if Field.PARENT_ID in json else None
        )
    
    def to_json(self):
        return {
            Field.FILES: [file.to_json() for file in self.files],
            Field.IGNORED_FILES: self.ignored_files,
            Field.SERVICE_ACCOUNT_FILE: self.service_account_file,
            Field.PARENT_ID: self.parent_id
        }