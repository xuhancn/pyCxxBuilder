import platform


# initialize variables for compilation
__IS_LINUX = platform.system() == "Linux"
__IS_DARWIN = platform.system() == "Darwin"
__IS_WINDOWS = platform.system() == "Windows"

__BUILD_TEMP_DIR = "CxxBuild"

class BuildTarget:
    __name = None
    __sources = [""]
    __definations = [""]
    __include_dirs = [""]
    __CFLAGS = [""]
    __LDFLAGS = [""]
    __libraries = [""]
    __build_directory = None
    __is_shared = False
    __is_static = True

    def __get_shared_flag(self):
        SHARED_FLAG = '/DLL' if __IS_WINDOWS else '-shared'
        return SHARED_FLAG

    def get_shared_lib_ext(self):
        SHARED_LIB_EXT = '.dll' if __IS_WINDOWS else '.so'
        return SHARED_LIB_EXT
    
    def get_static_lib_ext(self):
        STATIC_LIB_PREFIX = 'a' if __IS_WINDOWS else 'lib'
        return STATIC_LIB_PREFIX

    def get_exec_ext(self):
        EXEC_EXT = '.exe' if __IS_WINDOWS else ''
        return EXEC_EXT

    def __init__(self) -> None:
        pass

    def __prepare_build_parameters(self):
        cmd_include_dirs = [""]
        cmd_libraries = [""]
        cmd_definations = [""]
        cmd_cflags = [""]
        cmd_ldflags = [""]

        for inc in self.__include_dirs:
            cmd_include_dirs.append(f"-I{inc} ")

        for lib in self.__libraries:
            cmd_libraries.append(f"-L{inc} ")

        for defs in self.__definations:
            cmd_definations.append(f"-D{defs} ")

        for cflag in self.__CFLAGS:
            cmd_cflags.append(f"-{cflag} ")

        for ldflag in self.__LDFLAGS:
            cmd_ldflags.append(f"-{ldflag} ")

        return cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags


    def __compile(self) -> bool:
        pass

    def __link(self) -> bool:
        pass

    def add_sources(self, sources: list[str]):
        self.__sources += sources

    def add_libraries(self, libraries: list[str]):
        self.__libraries += libraries

    def add_definations(self, definations: list[str]):
        self.__definations += definations

    def add_cflags(self, cflags: list[str]):
        self.__CFLAGS += cflags

    def add_ldflags(self, ldflags: list[str]):
        self.__LDFLAGS += ldflags

    def target(self, 
              name: str,
              sources: list[str],
              definations: list[str] = None,
              include_dirs: list[str] = None,
              cflags: list[str] = None,
              ldflags: list[str] = None,
              libraries: list[str] = None,
              build_directory: str = None,
              is_shared: bool = True,
              is_static: bool = True
              ) -> bool:
        self.__name = name
        self.__sources = sources
        self.__definations = definations
        self.__include_dirs = include_dirs
        self.__CFLAGS = cflags
        self.__LDFLAGS = ldflags
        self.__libraries = libraries
        self.__build_directory = build_directory
        self.__is_shared = is_shared
        self.__is_static = is_static

    def build(self):
        if self.__name is None:
            raise ValueError("Target name should not be None.")

        cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags = self.__prepare_build_parameters()