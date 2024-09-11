class VideoNotFoundException(Exception):
    def __init__(self, message):
        super(VideoNotFoundException, self).__init__(message)
        self.message = message


class ExceedQuotaException(Exception):
    def __init__(self, message):
        super(ExceedQuotaException, self).__init__(message)
        self.message = message
