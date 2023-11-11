import platform
import os
from pathlib import Path
import errno

# initialize variables for compilation
__IS_LINUX = platform.system() == "Linux"
__IS_DARWIN = platform.system() == "Darwin"
__IS_WINDOWS = platform.system() == "Windows"

_BUILD_TEMP_DIR = "CxxBuild"

def _create_if_dir_not_exist(path_dir):
    if not os.path.exists(path_dir):
        try:
            Path(path_dir).mkdir(parents=True, exist_ok=True)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise RuntimeError("Fail to create path {}".format(path_dir))
            
def _remove_dir(path_dir):
    if os.path.exists(path_dir):
        for root, dirs, files in os.walk(path_dir, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.remove(file_path)
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.rmdir(dir_path)
        os.rmdir(path_dir)
            
def _check_if_file_exist(file_path):
    check_file = os.path.isfile(file_path)
    return check_file

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

    # File types
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
    
    def get_object_ext(self):
        OBJ_EXT = '.obj' if __IS_WINDOWS else '.o'
        return OBJ_EXT

    def __init__(self) -> None:
        pass
    
    # Build
    def __prepare_build_parameters(self):
        cmd_include_dirs = [""]
        cmd_libraries = [""]
        cmd_definations = [""]
        cmd_cflags = [""]
        cmd_ldflags = [""]

        if self.__include_dirs is not None:
            for inc in self.__include_dirs:
                cmd_include_dirs.append(f"-I{inc} ")

        if self.__libraries is not None:
            for lib in self.__libraries:
                cmd_libraries.append(f"-L{inc} ")

        if self.__definations is not None:
            for defs in self.__definations:
                cmd_definations.append(f"-D{defs} ")

        if self.__CFLAGS is not None:
            for cflag in self.__CFLAGS:
                cmd_cflags.append(f"-{cflag} ")

        if self.__LDFLAGS is not None:
            for ldflag in self.__LDFLAGS:
                cmd_ldflags.append(f"-{ldflag} ")

        return cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags


    def __compile(self, sources: list[str], cmd_include_dirs, cmd_definations, cmd_cflags, build_temp_dir) -> bool:
        for src in sources:
            print(src)

    def __link(self) -> bool:
        pass

    # Config
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

    # Major
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
            raise RuntimeError("Target name should not be None.")
        
        if self.__build_directory is None:
            build_root = os.path.dirname(os.path.abspath(__file__))
        else:
            build_root = self.__build_directory

        build_root = os.path.join(build_root, self.__name)
        build_temp_dir = os.path.join(build_root, _BUILD_TEMP_DIR)
        _create_if_dir_not_exist(build_root)
        _create_if_dir_not_exist(build_temp_dir)

        cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags = self.__prepare_build_parameters()

        self.__compile(self.__sources, cmd_include_dirs, cmd_definations, cmd_cflags, build_temp_dir)
