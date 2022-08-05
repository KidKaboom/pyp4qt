
class Callbacks(object):

    @staticmethod
    def validateSubmit():
        raise NotImplementedError

    @staticmethod
    def cleanupCallbacks():
        raise NotImplementedError

    @staticmethod
    def initCallbacks():
        raise NotImplementedError