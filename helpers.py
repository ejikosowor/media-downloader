import os, re
from dotenv import dotenv_values

from services.storage_service import LocalFileStrategy, SMBStrategy, StorageHandler, S3Strategy

ENV_VALUES = dotenv_values()

def extract_percentage(s):
    """Extracts percentage from string"""
    match = re.search(r'(\d+\.\d+%)', s)
    if match:
        return match.group(1)
    return None

def handle_upload(filename: str) -> dict | None:
    """Uploads file to storage service
        Args:
            filename (str): Name of the file
        Returns:
            dict | None: status and payload
    """

    storage_mode = ENV_VALUES["MODE"]

    storage_handler = StorageHandler(LocalFileStrategy())

    if storage_mode == "smb":
        storage_handler.set_strategy(SMBStrategy())
    elif storage_mode == "s3":
        storage_handler.set_strategy(S3Strategy())

    with open(filename, 'rb') as fd:
        try:
            storage_response = storage_handler.run(fd, filename.strip().replace(' ', '_'))
        finally:
            if storage_response["status"]:
                os.remove(filename)

    return storage_response

