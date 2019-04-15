"""
setup module for cyhy-mailer

Based on:

- https://packaging.python.org/distributing/
- https://github.com/pypa/sampleproject/blob/master/setup.py
"""

from setuptools import setup
from cyhy.mailer import __version__


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="cyhy-mailer",
    version=__version__,
    description="A tool for mailing out Cyber Hygiene, trustymail, and https-scan reports.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    # NCATS "homepage"
    url="https://www.us-cert.gov/resources/ncats",
    # The project's main homepage
    download_url="https://github.com/cisagov/cyhy-mailer",
    # Author details
    author="Cyber and Infrastructure Security Agency",
    author_email="ncats@hq.dhs.gov",
    license="License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # What does your project relate to?
    keywords="email sending,cyhy",
    packages=["cyhy.mailer"],
    install_requires=["boto3", "docopt", "mongo-db-from-config", "pystache"],
    extras_require={
        "test": ["coveralls", "pre-commit", "pytest", "pytest-cov", "semver"]
    },
    dependency_links=[
        "http://github.com/cisagov/mongo-db-from-config/tarball/develop#egg=mongo-db-from-config"
    ],
    entry_points={"console_scripts": ["cyhy-mailer = cyhy.mailer.cli:main"]},
)
