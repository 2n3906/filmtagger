"""
A simple CLI to tag film scans with EXIF metadata.
"""
from setuptools import find_packages, setup

setup(
    name='filmtagger',
    version='0.0.1',
    url='https://github.com/2n3906/filmtagger',
    license='MIT',
    author='Scott Johnston',
    author_email='sjohnston@alum.mit.edu',
    description='TA simple CLI to tag film scans with EXIF metadata.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    entry_points={
        'console_scripts': [
            'filmtagger = filmtagger.cli:main',
        ],
    },
    package_data={'filmtagger': ['*.toml']},
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
