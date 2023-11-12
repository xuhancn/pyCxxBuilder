import os
import CxxBuilder as cb

def get_files_in_dir(dir_path):
    file_list = []
    for file in os.listdir(dir_path):
        file_path = (os.path.join(dir_path, file))
        file_list.append(file_path)

    return file_list    

def build_mimalloc():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(curr_dir, "third_party", "mimalloc")

    source_files = get_files_in_dir(os.path.join(project_root, "src"))
    include_dirs = [os.path.join(project_root, "include"), os.path.join(project_root, "src")]

    cxx_target = cb.CxxBuilder.BuildTarget()
    cxx_target.target("libmimalloc", 
                      project_root = project_root,
                      sources = source_files, 
                      include_dirs= include_dirs
                      #  build_directory = "~",
                        )
    cxx_target.build()

    return


if __name__=='__main__':
    build_mimalloc()