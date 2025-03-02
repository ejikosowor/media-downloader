import streamlit as st
import logging, os, re, smbclient

from streamlit import spinner
from yt_dlp import YoutubeDL

smbclient.register_session(**st.secrets['smb'])

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def upload_to_smb(filename: str) -> None:
    """Uploads video to SMB share
    Args:
        filename (str): Name of the video file
    Returns:
        None
    """
    with open(filename, 'rb') as vd:
        video_bytes = vd.read()
        with smbclient.open_file(fr"""\\{st.secrets['smb']['server']}\shared\YT_Downloads\{filename}""", mode = "wb") as fd:
            fd.write(video_bytes)

    os.remove(filename)


def extract_percentage(s):
    """Extracts percentage from string"""
    match = re.search(r'(\d+\.\d+%)', s)
    if match:
        return match.group(1)
    return None


def cb_download_hook(d):
    """Callback function to handle download progress"""
    if d['status'] == 'downloading':
        percentage = extract_percentage(d['_percent_str']).split('%')[0]

    if d['status'] == 'finished':
        upload_to_smb(d['filename'])
        st.success("Download Complete!")


def write_human_response(user_query: str) -> None:
    """Write user query to chat"""
    with st.chat_message("human"):
        st.write(user_query)

def write_ai_response(user_query: str) -> None:
    """Write AI response to chat"""
    with st.chat_message("assistant"):
        with YoutubeDL({'progress_hooks': [cb_download_hook]}) as ydl:
            try:
                with spinner("Fetching Video Information"):
                    info = ydl.extract_info(user_query, download = False)
                    st.image(info['thumbnail'], width = 400)
                    st.markdown(f"""
                        **Title:** {info['title']}\n
                        **Video Duration:** {info['duration'] / 60} Minutes"""
                    )
                with spinner("Downloading Video"):
                    ydl.download([user_query])
            except Exception as e:
                st.write(f"{e}")


def main() -> None:
    st.set_page_config(page_title = "Home", layout = "wide", menu_items = None)

    header_container = st.container(key = "header_container")
    header_container.title("Youtube Downloader")

    if prompt := st.chat_input("Enter Video URL"):
        write_human_response(prompt)
        write_ai_response(prompt)


if __name__ == "__main__":
    main()