# media-downloader
A social media downloader

## Setting up
* Download latest version from [Github]() use default branch main
* In your terminal, navigate to the project directory and activate your virtual environment: 
    - Run `python -m venv virtual` to create virtual environment
    - Run `source virtual/bin/activate` (For MacOs/Linux) OR `virtual\Scripts\activate` (For Windows) to activate the virtual environment
* Create an `.env` file in the project directory using the `.env.sample` and set your downloads directory path:
    - `DOWNLOADS_DIR="/Users/john_doe/Downloads/"'`
* Install the required packages from `requirments.txt` from with in the virtual environment.
    - run `pip install -r requirements.txt` to install from requirements.txt file.
* Then run the app `streamlit run main.py`
