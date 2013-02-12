

class NotAllowed(Exception):

    def __init__(self, *args, **kwargs):
        self.permitted_methods = kwargs.pop('permitted_methods')


class InterruptPageProcessing(Exception):
    def __init__(self, cause):
        """
        :param cause: A NodeResponse
        """
        self.cause = cause


class ContentTypeUnsupported(Exception):
    pass
