import streamlit as st

from streamlit import spinner
from yt_dlp import YoutubeDL

from helpers import extract_percentage, handle_upload

progress_bar = None

def cb_download_hook(d):
    """Callback function to handle download progress"""
    global progress_bar
    if d['status'] == 'downloading':
        percent_str = extract_percentage(d['_percent_str'])
        percentage = float(percent_str.split('%')[0])
        progress_bar.progress(int(round(percentage, 0)), f"Downloading...{percent_str}")

    if d['status'] == 'finished':
        handler_response = handle_upload(d['filename'])
        if handler_response["status"]:
            markdown_url = """[Download Video]({})""".format(handler_response["payload"])
            st.success(f"""**Download Complete!**\n {markdown_url}""")
        else:
            st.success(f"""**Download Complete!**\n {handler_response["payload"]}""")


def write_human_response(user_query: str) -> None:
    """Write user query to chat"""
    with st.chat_message("human"):
        st.write(user_query)

def write_ai_response(user_query: str) -> None:
    """Write AI response to chat"""
    global progress_bar

    with st.chat_message("assistant"):
        with YoutubeDL({'progress_hooks': [cb_download_hook]}) as ydl:
            try:
                with spinner("Fetching Video Information"):
                    info = ydl.extract_info(user_query, download = False)
                    st.image(info['thumbnail'], width = 400)
                    st.markdown(f"""
                        **Title:** {info['title']}\n
                        **Video Duration:** {int(info['duration'] / 60)} Minutes"""
                    )
                with spinner("Downloading Video"):
                    if progress_bar is None:
                        progress_bar = st.progress(0)
                    ydl.download([user_query])
            except Exception as e:
                st.write(f"{e}")


def main() -> None:
    st.set_page_config(page_title = "Home", layout = "wide", menu_items = None)
    st.title("Youtube Downloader")

    if prompt := st.chat_input("Enter Video URL"):
        write_human_response(prompt)
        write_ai_response(prompt)


if __name__ == "__main__":
    main()