from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

from codecs import open

version = {}
with open("boardgamegeek/version.py") as fp:
    exec(fp.read(), version)

long_description = open("README.rst", encoding="utf-8").read()


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

tests_require = ["pytest", "pytest-mock"]

setup(
    name="bggapi",
    version=version["__version__"],
    packages=find_packages(),
    license="BSD",
    author="Aaron Cruz",
    author_email="g.aaroncruz@gmail.com",
    description="A Python interface to boardgamegeek.com's API",
    long_description=long_description,
    url="https://github.com/g-aaroncruz/boardgamegeek",
    tests_require=tests_require,
    extras_require={'test': tests_require},
    cmdclass={'test': PyTest},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=["requests>=2.3.0",
                      "requests-cache>=0.4.4",
                      "click>=8.1.7"],
    entry_points={
        "console_scripts": [
            "boardgamegeek = boardgamegeek.main:main"
        ]
    },
    python_requires='>=3.0'
)
