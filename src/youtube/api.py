import google_auth_oauthlib.flow as google_auth
import googleapiclient.discovery as google_client


class Youtube:
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    SCOPE = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    def __init__(self, client_secret_file):
        self.secret_file = client_secret_file
        self.youtube = self._build_google_api_client()

    def _build_google_api_client(self):
        flow = google_auth.flow.InstalledAppFlow.from_client_secrets_file(
            self.secret_file, self.SCOPE
        )
        credentials = flow.run_local_server()

        return google_client.build(
            self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials
        )

    def search_videos_by_api(self, query):
        raise NotImplementedError

    def search_videos_by_web_scraping(self, query):
        raise NotImplementedError
