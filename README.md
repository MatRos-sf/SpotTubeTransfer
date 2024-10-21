
# SpotiTube Transfer

This aplication was created to transfer own playlist from Spotify to YouTube. You can easly transfer your playlist only usind playlist ID.


## Tech Stack

![Python][py]

![Google][google]

![Pre-commit][p-commit]

![SQL][sql]

![Selenium][selenium]

[py]: https://img.shields.io/badge/python3.12-000000?style=for-the-badge&logo=python&logoColor=white
[google]: https://img.shields.io/badge/googleapis-000000?style=for-the-badge&logo=googleapist&logoColor=white
[p-commit]: https://img.shields.io/badge/pre-commit-000000?style=for-the-badge&logo=pre-commit&logoColor=white
[sql]: https://img.shields.io/badge/SQLAlchemy-000000?style=for-the-badge&SQLAlchemyt&logoColor=white
[selenium]: https://img.shields.io/badge/selenium-000000?style=for-the-badge&selenium&logoColor=white
## Getting Started


### Prerequisites
Before cloning the repository, you need to obtain two API keys:

* Create your Spotify API key by following this tutoral(section: **Create an app**) https://developer.spotify.com/documentation/web-api/tutorials/getting-started. Then obtain the access token by following the **Request an access token** section in the same link.
* Open your Google API console, create a project and then create your credential file (https://developers.google.com/youtube/registering_an_application#create_project)

This steps are required because the API keys will be used in the application.
### Installation
1. Clone the repo
```bash
git clone https://github.com/MatRos-sf/SpotTubeTransfer
```
2. Create a virtual enviroment
```bash
python3 -m venv venv
```
3. Install the required packages:
```
pip install -r requirements.txt
```
4. Build the .env file using the provided template:
```
CLIENT_ID=<spotify_client_id>
CLIENT_SECRET=<spotify_client_secret>
YT_CREDENTIAL_FILE_NAME=<path_to_youtobe_credential_file>
```
Make sure that the `.env` file and Youtube credentials are in the `src` folder.

### Running the app
You can run application with two different way:
1. using the bash script:
```
./spottube --id <id_playlist>
```
2. using the Python script
```
python3 main.py
```
## Optimizations

I use database to save YouTube song ID. In short, when we have the song, the app first checks the database to see if the song has been used before. If the song exists in the database, we retrieve its `id_song`. This process make the app faster, as we don't need to use Selenium every time to extract the song's ID.
