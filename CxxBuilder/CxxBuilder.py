import platform


# initialize variables for compilation
IS_LINUX = platform.system() == "Linux"
IS_DARWIN = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"


class CxxBuilder:
    __CFLAGS = None
    __SOURCES = None

    def __init__(self) -> None:
        pass

    def __compile(self) -> bool:
        pass

    def __link(self) -> bool:
        pass

    def add_sources(self, sources: list[str]):
        self.__SOURCES += sources

    def build(self) -> bool:
        pass