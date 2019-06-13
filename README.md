# Filmtagger
> A simple CLI to tag film scans with EXIF metadata.

A fuss-free way to take JPG files from film scanning and tag them with
date, camera, and film information for import into Lightroom (or equivalent).

## Installation

Install the package:

```
python3 setup.py install
```

## Usage examples

To set the date of all images to 12 June 2019, specifying camera and 
film as well:

    $ filmtagger -d 2019-06-12 -c "Leica M6" -f "E100G" *.jpg

Filmtagger supports fuzzy-matching against its database of cameras and films, so your input strings needn't be exact.  Likewise, it attempts to autodetect a variety of date input.
