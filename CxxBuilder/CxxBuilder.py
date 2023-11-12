import platform
import os
from pathlib import Path
import errno
import sys
import subprocess
from subprocess import check_call

import shlex

# initialize variables for compilation
_IS_LINUX = platform.system() == "Linux"
_IS_DARWIN = platform.system() == "Darwin"
_IS_WINDOWS = platform.system() == "Windows"

_BUILD_TEMP_DIR = "CxxBuild"

def _get_cxx_compiler():
    if _IS_WINDOWS:
        compiler = os.environ.get('CXX', 'cl')
    else:
        compiler = os.environ.get('CXX', 'c++')
    return compiler

def _create_if_dir_not_exist(path_dir):
    if not os.path.exists(path_dir):
        try:
            Path(path_dir).mkdir(parents=True, exist_ok=True)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise RuntimeError("Fail to create path {}".format(path_dir))
            
def _get_dir_name_from_path(file_path):
    dir_name = os.path.dirname(file_path)
    return dir_name
            
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

def _get_file_relative_path(project_root, src_file):
    relative_path = os.path.relpath(src_file, project_root)
    if relative_path is None:
        raise RuntimeError("source file {} is not belong to project {}".format(src_file, project_root))
    return relative_path

def run_command_line(cmd_line, cwd):
    cmd = shlex.split(cmd_line)
    status = subprocess.call(cmd, cwd=cwd, stderr=subprocess.STDOUT)
    
    return status

class BuildTarget:
    __name = None
    __project_root = None
    __sources = []
    __definations = []
    __include_dirs = []
    __CFLAGS = []
    __LDFLAGS = []
    __libraries = []
    __build_directory = None
    __is_shared = False
    __is_static = True

    # File types
    def __get_shared_flag(self):
        SHARED_FLAG = '/DLL' if _IS_WINDOWS else '-shared'
        return SHARED_FLAG

    def get_shared_lib_ext(self):
        SHARED_LIB_EXT = '.dll' if _IS_WINDOWS else '.so'
        return SHARED_LIB_EXT
    
    def __get_static_flag(self):
        STATIC_FLAG = '' if _IS_WINDOWS else '-static'
        return STATIC_FLAG

    def get_static_lib_ext(self):
        STATIC_LIB_PREFIX = 'a' if _IS_WINDOWS else 'lib'
        return STATIC_LIB_PREFIX

    def get_exec_ext(self):
        EXEC_EXT = '.exe' if _IS_WINDOWS else ''
        return EXEC_EXT
    
    def get_object_ext(self):
        OBJ_EXT = '.obj' if _IS_WINDOWS else '.o'
        return OBJ_EXT

    def __init__(self) -> None:
        pass
    
    # Build
    def __prepare_build_parameters(self):
        cmd_include_dirs = ""
        cmd_libraries = ""
        cmd_definations = ""
        cmd_cflags = ""
        cmd_ldflags = ""

        if self.__include_dirs is not None:
            for inc in self.__include_dirs:
                cmd_include_dirs += (f"-I{inc} ")

        if self.__libraries is not None:
            for lib in self.__libraries:
                cmd_libraries += (f"-L{inc} ")

        if self.__definations is not None:
            for defs in self.__definations:
                cmd_definations +=  (f"-D{defs} ")

        if self.__CFLAGS is not None:
            for cflag in self.__CFLAGS:
                cmd_cflags += (f"-{cflag} ")

        if self.__LDFLAGS is not None:
            for ldflag in self.__LDFLAGS:
                cmd_ldflags += (f"-{ldflag} ")

        return cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags


    def __compile(self, project_root, sources: list[str], cmd_include_dirs, cmd_definations, cmd_cflags, build_temp_dir):

        def _format_compile_cmd(compiler, src_file, output_obj, cmd_include_dirs, cmd_definations, cmd_cflags):
            cmd = f"{compiler} -c {src_file} {cmd_include_dirs} {cmd_definations} {cmd_cflags} -o {output_obj}"
            return cmd

        compiler = _get_cxx_compiler()
        obj_list = []
        for src in sources:
            relative_path = _get_file_relative_path(project_root, src)
            output_obj = os.path.join(build_temp_dir, relative_path)
            output_obj+= self.get_object_ext()

            _dir_name = _get_dir_name_from_path(output_obj)
            _create_if_dir_not_exist(_dir_name)

            compile_cmd = _format_compile_cmd(compiler, src, output_obj, cmd_include_dirs, cmd_definations, cmd_cflags)
            print(compile_cmd)
            run_command_line(compile_cmd, build_temp_dir)

            obj_list.append(output_obj)
        return obj_list

    def __link(self, obj_list: list[str]) -> bool:
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
              project_root: str,
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
        self.__project_root = project_root
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
            raise RuntimeError("target name should not be None.")
        
        if self.__project_root is None:
            raise RuntimeError("project_root should not be None.")        
        
        if self.__build_directory is None:
            build_root = os.path.dirname(os.path.abspath(__file__))
        else:
            build_root = self.__build_directory

        build_root = os.path.join(build_root, self.__name)
        build_temp_dir = os.path.join(build_root, _BUILD_TEMP_DIR)
        _create_if_dir_not_exist(build_root)
        _create_if_dir_not_exist(build_temp_dir)

        cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags = self.__prepare_build_parameters()

        obj_list = self.__compile(project_root = self.__project_root, 
                       sources=self.__sources, cmd_include_dirs=cmd_include_dirs, 
                       cmd_definations=cmd_definations, cmd_cflags=cmd_cflags, build_temp_dir=build_temp_dir)
        
        self.__link(obj_list=obj_list)
        

