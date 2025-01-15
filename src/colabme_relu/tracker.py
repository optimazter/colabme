


class Field:
    FILES = "files"
    SERVICE_ACCOUNT_FILE = "service_account_file"
    PARENT_ID = "parent_id"


class Tracker:

    def __init__(self, files: dict = {}, service_account_file: str = None, parent_id: str = None):
        self.files = files
        self.service_account_file = service_account_file
        self.parent_id = parent_id

    def from_json(json):
        return Tracker(
            files = json[Field.FILES],
            service_account_file= json[Field.SERVICE_ACCOUNT_FILE],
            parent_id = json[Field.PARENT_ID]
        )
    
    def to_json(self):
        return {
            Field.FILES: self.files,
            Field.SERVICE_ACCOUNT_FILE: self.service_account_file,
            Field.PARENT_ID: self.parent_id
        }