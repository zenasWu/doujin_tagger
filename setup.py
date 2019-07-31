import os
from setuptools import setup, find_packages


HERE = os.path.dirname(os.path.realpath(__file__))

def long_description():
    with open("README.rst", "rb") as f:
        return f.read().decode("utf-8")

setup(
    name="doujin_tagger",
    version="0.1.0",
    author="maybeRainH",
    author_email="gooloo911110@gmail.com",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description="a doujin voice tagger based on dlsite info",
    entry_points={
        "console_scripts": [
            "doutag = doujin_tagger.main:main",
        ]
    },
    long_description=long_description(),
    long_description_content_type="text/x-rst",
    license="MIT",
    url="https://github.com/caiheyao/doujin_tagger",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    setup_requires=['pytest-runner',],
    install_requires=['requests', 'lxml', 'mutagen', 'pillow'],
    tests_require=["pytest", "pytest-cov", "testfixtures"],
    include_package_data=True,
    zip_safe=False,
)
