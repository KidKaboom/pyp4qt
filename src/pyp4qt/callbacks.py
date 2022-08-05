# Project Modules


# Python Modules


if __name__ == "__main__":
    pass


class BaseCallbacks(object):

    @staticmethod
    def validateSubmit():
        raise NotImplementedError

    @staticmethod
    def cleanupCallbacks():
        raise NotImplementedError

    @staticmethod
    def initCallbacks():
        raise NotImplementedError