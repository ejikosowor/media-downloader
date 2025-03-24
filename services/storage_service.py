import boto3, smbclient

from abc import ABC, abstractmethod
from dotenv import dotenv_values
from typing import BinaryIO

ENV_VALUES = dotenv_values()

class StorageStrategy(ABC):
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

class SMBStrategy(StorageStrategy):
    def __init__(self,):
        self.credentials = {
            "server": ENV_VALUES["SMB_HOST"],
            "username": ENV_VALUES["SMB_USERNAME"],
            "password": ENV_VALUES["SMB_PASSWORD"]
        }

    def upload(self, file: BinaryIO, filename: str) -> dict:
        smbclient.register_session(**self.credentials)
        smb_fileshare = fr"""\\{self.credentials['server']}\shared\YT_Downloads\{filename}"""

        try:
            with smbclient.open_file(smb_fileshare, mode = "wb") as smb_fd:
                smb_fd.write(file.read())
            return { "status": True, "payload": smb_fileshare }
        except Exception as e:
            return { "status": True, "payload": str(e) }

class S3Strategy(StorageStrategy):
    def __init__(self,):
        self.credentials = {
            "bucket": ENV_VALUES["AWS_BUCKET"],
            "region": ENV_VALUES["AWS_REGION"],
            "aws_access_key_id": ENV_VALUES["AWS_ACCESS_KEY_ID"],
            "aws_secret_access_key": ENV_VALUES["AWS_SECRET_ACCESS_KEY"]
        }

    def upload(self, file: BinaryIO, filename: str) -> dict:
        try:
            session = boto3.Session(
                region_name = self.credentials["region"],
                aws_access_key_id = self.credentials["aws_access_key_id"],
                aws_secret_access_key = self.credentials["aws_secret_access_key"],
                )
            s3 = session.client("s3")

            try:
                s3.put_object(Body = file, Bucket = self.credentials["bucket"], Key = filename, ContentType = "video/mp4")
                url = f"https://{self.credentials['bucket']}.s3.{self.credentials['region']}.amazonaws.com/{filename}"
                return { "status": True, "payload": url }
            except Exception as e:
                return {"status": False, "payload": f"Error uploading media to S3: {e}"}
        except Exception as e:
            return {"status": False, "payload": str(e)}

class StorageHandler:
    def __init__(self, strategy: StorageStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: StorageStrategy):
        self._strategy = strategy

    def run(self, file: BinaryIO, filename: str) -> dict:
        return self._strategy.upload(file, filename)
