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

Filmtagger supports fuzzy-matching against its database of cameras and 
films, so your input strings needn't be exact.  Likewise, it attempts to 
autodetect a variety of date/time input.

## Configuration

You may configure your own camera and film definitions to override the
system-wide ones.

Create a `~/.config/filmtagger/cameras.toml` file that looks like this:

```toml
["Mamiya RB67"]
"Exif.Image.Make" = "Mamiya"
"Exif.Image.Model" = "RB67"
```

And a `~/.config/filmtagger/films.toml` like this:

```toml
["Ilford HP5 Plus"]
"Exif.Photo.ISOSpeedRatings" = 400
"Xmp.AnalogExif.FilmMaker" = "Ilford"
"Xmp.iptcExt.DigitalSourceType" = "http://cv.iptc.org/newscodes/digitalsourcetype/negativeFilm"
```

The section headings will be fuzzy-matched from the command-line 
arguments.  The key-value pairs that follow will be set as metadata, 
assuming they are [valid tag names](https://exiv2.org/metadata.html).
In addition to the standard Exiv2 tag schema, [AnalogExif 
tags](http://analogexif.sourceforge.net/help/analogexif-xmp.php) are 
also supported.
