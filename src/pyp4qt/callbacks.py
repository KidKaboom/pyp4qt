class Callbacks(object):

    @staticmethod
    def validate_submit():
        raise NotImplementedError

    @staticmethod
    def cleanup_callbacks():
        raise NotImplementedError

    @staticmethod
    def init_callbacks():
        raise NotImplementedError
