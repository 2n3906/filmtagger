"""
A simple CLI to tag film scans with EXIF metadata.
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="filmtagger",
    version="0.0.3",
    url="https://github.com/2n3906/filmtagger",
    license="MIT",
    author="Scott Johnston",
    author_email="sjohnston@alum.mit.edu",
    description="A simple CLI to tag film scans with EXIF metadata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        "click",
        "toml",
        "fuzzywuzzy",
        "python-Levenshtein",
        "python_dateutil",
        "xdg",
        "PyGObject",
    ],
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
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ])
