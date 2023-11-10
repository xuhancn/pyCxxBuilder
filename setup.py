from setuptools import setup
import os

PACKAGE_NAME = "CxxBuilder"

cxx_builder_build_version = 0.1

long_description = ""
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

def _build_installation_dependency():
    install_requires = []
    install_requires.append("psutil")
    install_requires.append("numpy")
    install_requires.append("packaging")
    return install_requires

ext_modules = []

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
    # cmdclass=cmdclass,
    # entry_points=entry_points,
    license="https://www.apache.org/licenses/LICENSE-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
)