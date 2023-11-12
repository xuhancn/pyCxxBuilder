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

    if (False):
        # From mimalloc CMakeLists.txt, we need compile sources in fix order.
        source_files = get_files_in_dir(os.path.join(project_root, "src"))
    else:
        source_root = os.path.join(project_root, "src")
        source_files = [os.path.join(source_root, "alloc.c"),
                        os.path.join(source_root, "alloc-aligned.c"),
                        os.path.join(source_root, "alloc-posix.c"),
                        os.path.join(source_root, "arena.c"),
                        os.path.join(source_root, "bitmap.c"),
                        os.path.join(source_root, "heap.c"),
                        os.path.join(source_root, "init.c"),
                        os.path.join(source_root, "options.c"),
                        os.path.join(source_root, "os.c"),
                        os.path.join(source_root, "page.c"),
                        os.path.join(source_root, "random.c"),
                        os.path.join(source_root, "segment.c"),
                        os.path.join(source_root, "segment-map.c"),
                        os.path.join(source_root, "stats.c"),
                        os.path.join(source_root, "prim", "prim.c"),
                        ]

    include_dirs = [os.path.join(project_root, "include"), os.path.join(project_root, "src")]

    cxx_target = cb.CxxBuilder.BuildTarget()
    cxx_target.target("libmimalloc", 
                      project_root = project_root,
                      sources = source_files, 
                      include_dirs= include_dirs
                      #  build_directory = "~",
                        )
    # cxx_target.add_definations("MI_MALLOC_OVERRIDE")
    cxx_target.add_defination("MI_STATIC_LIB")
    if cxx_target.is_linux():
        cxx_target.add_cflags(["-fPIC", "-Wall"])
    cxx_target.build()

    return


if __name__=='__main__':
    build_mimalloc()