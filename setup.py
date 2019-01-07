"""
setup module for cyhy-mailer

Based on:

- https://github.com/dhs-ncats/cyhy-mailer
"""

from setuptools import setup
from cyhy.mailer import __version__


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='cyhy-mailer',
    version=__version__,
    description='A tool for mailing out Cyber Hygiene, trustymail, and https-scan reports.',
    long_description=readme(),
    long_description_content_type='text/markdown',

    # NCATS "homepage"
    url='https://www.dhs.gov/cyber-incident-response',
    # The project's main homepage
    download_url='https://github.com/dhs-ncats/cyhy-mailer',

    # Author details
    author='Department of Homeland Security, National Cybersecurity Assessments and Technical Services team',
    author_email='ncats@hq.dhs.gov',

    license='License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='email sending,cyhy',

    packages=['cyhy.mailer'],

    install_requires=[
        'boto3>=1.9.74'
        'docopt>=0.6.2',
        'pymongo>=3.6.1',
        'pystache>=0.5.4',
        'pyyaml>=3.12'
    ],

    extras_require={
        'dev': [
            'check-manifest>=0.36',
            'pytest>=3.5.0',
            'semver>=2.7.9',
            'tox>=3.0.0',
            'wheel>=0.31.0'
        ],
    },

    entry_points={
        'console_scripts': [
            'cyhy-mailer = cyhy.mailer.cli:main'
        ]
    }
)
