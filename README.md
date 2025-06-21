# filmtagger

A simple CLI to tag film scans with EXIF metadata.

## Installation

```bash
pip install filmtagger
```

### Requirements

This package uses the [pyexiv2](https://pypi.org/project/pyexiv2/) library for EXIF/XMP metadata manipulation, which provides Python bindings for the Exiv2 library. The pyexiv2 package includes pre-compiled binaries for most platforms, making installation straightforward without requiring system-level dependencies.

## Usage

```bash
# Show help
filmtagger --help

# Tag a single image
filmtagger tag image.jpg

# Tag multiple images
filmtagger tag *.jpg
```

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development and package management.

### Setup Development Environment

1. Install Hatch:
```bash
pip install hatch
```

2. Create and activate development environment:
```bash
hatch shell
```

### Running Tests

```bash
# Run all tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run linting checks
hatch run lint:all

# Format code
hatch run lint:fmt
```

### Building and Publishing

```bash
# Build the package
hatch build

# Publish to PyPI
hatch publish
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

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
