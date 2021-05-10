from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="inter-morse",
    version="1.0.1",
    description="Interpret wav audio files to Morse code and translate it.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cnyllou/inter-morse",
    author="Cnyllou",
    author_email="cnyllou@gmail.com",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["inter_morse"],
    include_package_data=True,
    install_requires=["pydub", "matplotlib"],
    entry_points={
        "console_scripts": [
            "inter-morse=inter_morse.__main__:main",
        ]
    },
    project_urls={
        'Source': 'https://github.com/cnyllou/inter-morse/',
        'Tracker': 'https://github.com/cnyllou/inter-morse/issues',
    },
)
