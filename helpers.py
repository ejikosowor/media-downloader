import os, re
from dotenv import dotenv_values

from services.storage_service import SMBStrategy, StorageHandler, S3Strategy

ENV_VALUES = dotenv_values()

def extract_percentage(s):
    """Extracts percentage from string"""
    match = re.search(r'(\d+\.\d+%)', s)
    if match:
        return match.group(1)
    return None

def handle_upload(filename: str) -> dict | None:
    if ENV_VALUES["MODE"] == "local":
        storage_handler = StorageHandler(SMBStrategy())
    else:
        storage_handler = StorageHandler(S3Strategy())

    with open(filename, 'rb') as fd:
        try:
            storage_response = storage_handler.run(fd, filename)
        except Exception as e:
            storage_response = {
                "status": False,
                "payload": "Failed to Upload Downloaded Video.\n{}".format(e)
            }
        finally:
            if storage_response["status"]:
                os.remove(filename)

    return storage_response

