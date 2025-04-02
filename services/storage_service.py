import boto3, os, smbclient, urllib.parse

from abc import ABC, abstractmethod
from dotenv import dotenv_values
from typing import BinaryIO

ENV_VALUES = dotenv_values()

class StorageStrategy(ABC):
    download_path = None

    @abstractmethod
    def upload(self, file: BinaryIO, filename: str) -> dict:
        """Uploads file to a storage service
            Args:
                file (BinaryIO): File to upload
                filename (str): Name of the file
            Returns:
                dict: status and payload
        """
        pass

    def response_message(self, protocol: str) -> dict:
        """Returns the response message
            Args:
                protocol (str): Protocol used for the response
            Returns:
                dict: response message
        """
        return { "status": True, "payload": f"{protocol}{self.download_path}" }

class SMBStrategy(StorageStrategy):
    def __init__(self):
        smbclient.register_session(
            server = ENV_VALUES['SMB_HOST'],
            username = ENV_VALUES['SMB_USERNAME'],
            password = ENV_VALUES['SMB_PASSWORD']
        )
        self.download_path = f"//{ENV_VALUES['SMB_HOST']}/shared/YT_Downloads/"

    def upload(self, file: BinaryIO, filename: str) -> dict:
        try:
            with smbclient.open_file(fr"{self.download_path}{filename}", mode = "wb") as smb_fd:
                smb_fd.write(file.read())
            return self.response_message("smb:")
        except Exception as e:
            return { "status": True, "payload": f"SMB upload failed: {e}"}

class S3Strategy(StorageStrategy):
    def __init__(self):
        self.credentials = {
            "bucket": ENV_VALUES["AWS_BUCKET"],
            "region": ENV_VALUES["AWS_REGION"],
            "aws_access_key_id": ENV_VALUES["AWS_ACCESS_KEY_ID"],
            "aws_secret_access_key": ENV_VALUES["AWS_SECRET_ACCESS_KEY"]
            }
        self.download_path = f"{self.credentials['bucket']}.s3.{self.credentials['region']}.amazonaws.com/"

    def upload(self, file: BinaryIO, filename: str) -> dict:
        session = boto3.Session(
            region_name = self.credentials["region"],
            aws_access_key_id = self.credentials["aws_access_key_id"],
            aws_secret_access_key = self.credentials["aws_secret_access_key"],
            )
        s3 = session.client("s3")

        try:
            s3.put_object(Body = file, Bucket = self.credentials["bucket"], Key = filename, ContentType = "video/mp4")

            self.download_path = self.download_path + urllib.parse.quote_plus(filename)
            return self.response_message("https://")
        except Exception as e:
            return {"status": False, "payload": f"Error uploading media to S3: {e}"}

class LocalFileStrategy(StorageStrategy):
    def __init__(self):
        self.download_path = ENV_VALUES["DOWNLOADS_DIR"]

    def upload(self, file: BinaryIO, filename: str) -> dict:
        try:
            file_path = os.path.join(self.download_path, filename)

            with open(file_path, "wb") as local_file:
                local_file.write(file.read())
            return self.response_message("file://")
        except Exception as e:
            return { "status": False, "payload": str(e) }

class StorageHandler:
    def __init__(self, strategy: StorageStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: StorageStrategy):
        self._strategy = strategy

    def run(self, file: BinaryIO, filename: str) -> dict:
        return self._strategy.upload(file, filename)
