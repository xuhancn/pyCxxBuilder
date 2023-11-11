import os
import CxxBuilder as cb

def get_files_in_dir(dir_path):
    file_list = []
    for file in os.listdir(dir_path):
        file_path = (os.path.join(dir_path, file))
        file_list.append(file_path)

    return file_list    

def build_libxsmm():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    libxsmm_root = os.path.join(curr_dir, "third_party", "libxsmm")

    source_files = get_files_in_dir(os.path.join(libxsmm_root, "src"))
    include_files = get_files_in_dir(os.path.join(libxsmm_root, "include"))

    cxx_target = cb.CxxBuilder.BuildTarget()
    cxx_target.target("libxsmm", 
                      project_root = libxsmm_root,
                      sources = source_files, 
                      include_dirs= include_files,
                      #  build_directory = "~",
                        )
    cxx_target.build()

    return


if __name__=='__main__':
    build_libxsmm()