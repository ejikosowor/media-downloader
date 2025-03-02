import os, re, smbclient


def extract_percentage(s):
    """Extracts percentage from string"""
    match = re.search(r'(\d+\.\d+%)', s)
    if match:
        return match.group(1)
    return None


def upload_to_smb(filename: str, credentials: dict) -> None:
    """Uploads file to SMB share
    Args:
        filename (str): Name of the file
        credentials (dict): SMB credentials
    Returns:
        None
    """
    smbclient.register_session(**credentials)
    smb_fileshare = fr"""\\{credentials['server']}\shared\YT_Downloads\{filename}"""

    with open(filename, 'rb') as fd:
        file_bytes = fd.read()
        with smbclient.open_file(smb_fileshare, mode = "wb") as smb_fd:
            smb_fd.write(file_bytes)
    os.remove(filename)