import os

from dotenv import load_dotenv

from src.database.connection import Database, STdb
from src.spot_tube import SpotTube

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
YT_CREDENTIAL_FILE_NAME = os.getenv("YT_CREDENTIAL_FILE_NAME")


def main():
    st = SpotTube(CLIENT_ID, CLIENT_SECRET, YT_CREDENTIAL_FILE_NAME, STdb(Database()))
    st.run()


if __name__ == "__main__":
    main()
