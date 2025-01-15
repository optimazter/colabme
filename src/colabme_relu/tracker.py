


class Field:
    FILES = "files"
    IGNORED_FILES = "ignored_files"
    SERVICE_ACCOUNT_FILE = "service_account_file"
    PARENT_ID = "parent_id"


class Tracker:

    def __init__(self, files: dict = {}, ignored_files: list = [], service_account_file: str = None, parent_id: str = None):
        self.files = files
        self.ignored_files = ignored_files
        self.service_account_file = service_account_file
        self.parent_id = parent_id

    def from_json(json):
        return Tracker(
            files = json[Field.FILES],
            ignored_files= json[Field.IGNORED_FILES],
            service_account_file= json[Field.SERVICE_ACCOUNT_FILE],
            parent_id = json[Field.PARENT_ID]
        )
    
    def to_json(self):
        return {
            Field.FILES: self.files,
            Field.IGNORED_FILES: self.ignored_files,
            Field.SERVICE_ACCOUNT_FILE: self.service_account_file,
            Field.PARENT_ID: self.parent_id
        }