from setuptools import setup, find_packages
from mezzanine_agenda import __version__
import subprocess

def get_long_desc():
    """Use Pandoc to convert the readme to ReST for the PyPI."""
    try:
        return subprocess.check_output(['pandoc', '-f', 'markdown', '-t', 'rst', 'README.mdown'])
    except:
        print "WARNING: The long readme wasn't converted properly"

setup(name='mezzanine-agenda',
    version=__version__,
    description='Events for the Mezzanine CMS',
    long_description=get_long_desc(),
    author='James Pells',
    author_email='jimmy@jamespells.com',
    url='https://github.com/jpells/mezzanine-agenda',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        'setuptools_git>=0.3',
    ],
    install_requires=[
        'mezzanine',
        'icalendar==3.0.1b2',
        'geopy==0.95.1',
        'pytz',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
