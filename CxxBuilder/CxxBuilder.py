import platform
import os
from pathlib import Path
import errno
import sys
import subprocess
from subprocess import check_call

import shlex

# initialize variables for compilation
_IS_LINUX = sys.platform.startswith('linux')
_IS_MACOS = sys.platform.startswith('darwin')
_IS_WINDOWS = sys.platform == 'win32'

_BUILD_TEMP_DIR = "CxxBuild"

def _get_cxx_compiler():
    if _IS_WINDOWS:
        compiler = os.environ.get('CXX', 'cl')
    else:
        compiler = os.environ.get('CXX', 'c++')
    return compiler

def _get_cxx_linker():
    if _IS_WINDOWS:
        compiler = os.environ.get('CXX', 'link')
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

def run_command_line(cmd_line, cwd=None):
    cmd = shlex.split(cmd_line)
    status = subprocess.call(cmd, cwd=cwd, stderr=subprocess.STDOUT)
    
    return status

def _get_windows_runtime_libs():
    return ["psapi", "shell32", "user32", "advapi32", "bcrypt",
            "kernel32", "user32", "gdi32", "winspool", "shell32", 
            "ole32", "oleaut32", "uuid", "comdlg32", "advapi32"]

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
    # OS info
    def is_windows(self):
        return _IS_WINDOWS
    
    def is_linux(self):
        return _IS_LINUX
    
    def is_mac_os(self):
        return _IS_MACOS

    # File types
    def __get_shared_flag(self):
        SHARED_FLAG = 'DLL' if _IS_WINDOWS else 'shared'
        return SHARED_FLAG

    def get_shared_lib_ext(self):
        SHARED_LIB_EXT = '.dll' if _IS_WINDOWS else '.so'
        return SHARED_LIB_EXT
    
    def __get_static_flag(self):
        STATIC_FLAG = '' if _IS_WINDOWS else 'static'
        return STATIC_FLAG

    def get_static_lib_ext(self):
        STATIC_LIB_PREFIX = '.lib' if _IS_WINDOWS else '.a'
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

        if len(self.__include_dirs) != 0:
            for inc in self.__include_dirs:
                if _IS_WINDOWS:
                    cmd_include_dirs += (f"/I {inc} ")
                else:
                    cmd_include_dirs += (f"-I{inc} ")

        if len(self.__libraries) != 0:
            for lib in self.__libraries:
                if _IS_WINDOWS:
                    cmd_libraries += (f"{lib}.lib ")
                else:
                    cmd_libraries += (f"-L{lib} ")

        if len(self.__definations) != 0:
            for defs in self.__definations:
                if _IS_WINDOWS:
                    cmd_definations +=  (f"/D {defs} ")
                else:
                    cmd_definations +=  (f"-D{defs} ")

        if len(self.__CFLAGS) != 0:
            for cflag in self.__CFLAGS:
                if _IS_WINDOWS:
                    cmd_cflags += (f"/{cflag} ")
                else:
                    cmd_cflags += (f"-{cflag} ")

        if len(self.__LDFLAGS) != 0:
            for ldflag in self.__LDFLAGS:
                if _IS_WINDOWS:
                    cmd_ldflags += (f"/{ldflag} ")
                else:    
                    cmd_ldflags += (f"-{ldflag} ")

        return cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags


    def __compile(self, project_root, sources: list[str], cmd_include_dirs, cmd_definations, cmd_cflags, build_temp_dir):

        def _format_compile_cmd(compiler, src_file, output_obj, cmd_include_dirs, cmd_definations, cmd_cflags):
            if _IS_WINDOWS:
                # https://stackoverflow.com/questions/36472760/how-to-create-obj-file-using-cl-exe
                cmd = f"{compiler} /c {src_file} {cmd_include_dirs} {cmd_definations} {cmd_cflags} /Fo{output_obj}"
                cmd = cmd.replace("\\", "\\\\")
            else:
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
            print("!!! compile_cmd: ", compile_cmd)
            run_command_line(compile_cmd, build_temp_dir)

            obj_list.append(output_obj)
        return obj_list

    def __link(self, obj_list: list[str], cmd_ldflags, cmd_libraries, target_file) -> bool:
        def _format_link_cmd(linker, obj_list_str, cmd_ldflags, cmd_libraries, target_file):
            if _IS_WINDOWS:
                # https://stackoverflow.com/questions/2727187/creating-dll-and-lib-files-with-the-vc-command-line
                cmd = f"{linker} {obj_list_str} {cmd_ldflags} {cmd_libraries} /OUT:{target_file}"
                cmd = cmd.replace("\\", "\\\\")
            else:
                cmd = f"{linker} {obj_list_str} {cmd_ldflags} {cmd_libraries} -o {target_file}"
            return cmd
        
        linker = _get_cxx_linker()
        obj_list_str = shlex.join(obj_list)

        link_cmd = _format_link_cmd(linker, obj_list_str, cmd_ldflags, cmd_libraries, target_file)
        print("!!! link cmd: ", link_cmd)
        run_command_line(link_cmd)

    # Config
    def add_sources(self, sources: list[str]):
        for i in sources:
            self.__sources.append(i)

    def add_libraries(self, libraries: list[str]):
        for i in libraries:
            self.__libraries.append(i)

    def add_definations(self, definations: list[str]):
        for i in definations:
            self.__definations.append(i)

    def add_defination(self, defination: str, value:str = ""):
        define = f"{defination}={value}" if value != "" else f"{defination}"
        self.__definations.append(define)

    def add_cflags(self, cflags: list[str]):
        for i in cflags:
            self.__CFLAGS.append(i)

    def add_ldflags(self, ldflags: list[str]):
        for i in ldflags:
            self.__LDFLAGS.append(i)

    # Major
    def target(self, 
              name: str,
              project_root: str,
              sources: list[str],
              definations: list[str] = [],
              include_dirs: list[str] = [],
              cflags: list[str] = [],
              ldflags: list[str] = [],
              libraries: list[str] = [],
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

        if self.__is_shared:
            if self.__is_static:
                file_ext = self.get_static_lib_ext()
                self.add_ldflags([self.__get_shared_flag()])
            else:
                file_ext = self.get_shared_lib_ext()
                self.add_ldflags([self.__get_shared_flag()])
        else:
            file_ext = self.get_exec_ext()

        if _IS_WINDOWS:
            self.add_libraries(_get_windows_runtime_libs())

        build_root = os.path.join(build_root, self.__name)
        build_temp_dir = os.path.join(build_root, _BUILD_TEMP_DIR)
        _create_if_dir_not_exist(build_root)
        _create_if_dir_not_exist(build_temp_dir)

        cmd_include_dirs, cmd_libraries, cmd_definations, cmd_cflags, cmd_ldflags = self.__prepare_build_parameters()

        obj_list = self.__compile(project_root = self.__project_root, 
                       sources=self.__sources, cmd_include_dirs=cmd_include_dirs, 
                       cmd_definations=cmd_definations, cmd_cflags=cmd_cflags, build_temp_dir=build_temp_dir)

        target_file = f"{self.__name}{file_ext}"
        target_file = os.path.join(build_root, target_file)
        self.__link(obj_list=obj_list, cmd_ldflags=cmd_ldflags, cmd_libraries=cmd_libraries, target_file=target_file)
        

