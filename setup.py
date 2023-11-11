import setuptools.command.install
from setuptools import setup
import shutil
import os

PACKAGE_NAME = "CxxBuilder"

cxx_builder_build_version = 0.1

long_description = ""
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

def _build_installation_dependency():
    install_requires = []
    return install_requires

ext_modules = []

class install(setuptools.command.install.install):
    def run(self):
        super().run()


class clean(setuptools.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import glob
        import re

        with open(".gitignore") as f:
            ignores = f.read()
            pat = re.compile(r"^#( BEGIN NOT-CLEAN-FILES )?")
            for wildcard in filter(None, ignores.split("\n")):
                match = pat.match(wildcard)
                if match:
                    if match.group(1):
                        # Marker is found and stop reading .gitignore.
                        break
                    # Ignore lines which begin with '#'.
                else:
                    # Don't remove absolute paths from the system
                    wildcard = wildcard.lstrip("./")

                    for filename in glob.glob(wildcard):
                        try:
                            os.remove(filename)
                        except OSError:
                            shutil.rmtree(filename, ignore_errors=True)

cmdclass = {
    # "bdist_wheel": wheel_concatenate,
    # "build_ext": build_ext,
    "clean": clean,
    "install": install,
    # "sdist": sdist,
}

setup(
    name=PACKAGE_NAME,
    version=cxx_builder_build_version,
    description="python Cxx Builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuhancn/pyCxxBuilder",
    author="Intel Corp.",
    install_requires=_build_installation_dependency(),
    packages=[PACKAGE_NAME],
    package_data={PACKAGE_NAME: ["*.so", "lib/*.so", "bin/*.dll", "lib/*.lib"]},
    zip_safe=False,
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    # entry_points=entry_points,
    license="https://www.apache.org/licenses/LICENSE-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
)