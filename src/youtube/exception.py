class VideoNotFoundException(Exception):
    def __init__(self, message):
        super(VideoNotFoundException, self).__init__(message)
        self.message = message
