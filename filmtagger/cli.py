import importlib.resources
import os
import sys
from pathlib import Path

import click

# import re
import gi
import toml
from dateutil import parser
from fuzzywuzzy import process

gi.require_version("GExiv2", "0.10")
from gi.repository import GExiv2

# Load system-wide camera & film definitions
with importlib.resources.open_text(__name__, "cameras.toml") as f:
    cameras = toml.load(f)
with importlib.resources.open_text(__name__, "films.toml") as f:
    films = toml.load(f)

# Load user-provided camera & film definitions and merge
# Config files should be stored in:
#     (UNIX)  ~/.config/filmtagger/*.toml
#     (Win32) C:\Users\username\AppData\Roaming\filmtagger\*.toml
if sys.platform == "win32":
    CAMERA_CONFIG_FILE = Path(
        os.environ.get("APPDATA")) / "filmtagger" / "cameras.toml"
    FILM_CONFIG_FILE = Path(
        os.environ.get("APPDATA")) / "filmtagger" / "films.toml"
else:
    configpath = Path(os.environ.get("HOME")) / ".config"
    if os.environ.get("XDG_CONFIG_HOME"):
        configpath = Path(os.environ.get("XDG_CONFIG_HOME"))
    CAMERA_CONFIG_FILE = configpath / "filmtagger" / "cameras.toml"
    FILM_CONFIG_FILE = configpath / "filmtagger" / "films.toml"

if Path(CAMERA_CONFIG_FILE).is_file():
    try:
        user_cameras = toml.load(CAMERA_CONFIG_FILE)
        cameras = {**cameras, **user_cameras}
    except toml.decoder.TomlDecodeError:
        print(f"File {CAMERA_CONFIG_FILE} is not valid TOML.")
        sys.exit(1)
if Path(FILM_CONFIG_FILE).is_file():
    try:
        user_films = toml.load(FILM_CONFIG_FILE)
        films = {**cameras, **user_films}
    except toml.decoder.TomlDecodeError:
        print(f"File {FILM_CONFIG_FILE} is not valid TOML.")
        sys.exit(1)


def validate_date(ctx, param, value):
    if value is not None:
        try:
            date = parser.parse(value)
            return date
        except ValueError:
            raise click.BadParameter("Could not parse date.")
    else:
        return value


def validate_camera(ctx, param, value):
    if value is not None:
        match = process.extractOne(value, cameras.keys(), score_cutoff=80)
        if match:
            return match[0]
        else:
            raise click.BadParameter("Camera not found in database.")
    else:
        return value


def validate_film(ctx, param, value):
    if value is not None:
        match = process.extractOne(value, films.keys(), score_cutoff=80)
        if match:
            return match[0]
        else:
            raise click.BadParameter("Film not found in database.")
    else:
        return value


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
@click.option(
    "--date", "-d", help="Date of image capture.", callback=validate_date)
@click.option("--camera", "-c", help="Camera name.", callback=validate_camera)
@click.option("--film", "-f", help="Film name.", callback=validate_film)
@click.option(
    "--iso",
    "-i",
    help="ISO rating (overrides film definition)",
    type=click.INT)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def main(camera, date, film, iso, files):
    """Tag scanned images with film-specific EXIF metadata."""

    if date:
        exif_datetime = date.strftime("%Y:%m:%d %H:%M:%S")
        click.echo(f"Set dates to:  {date}")
    if camera:
        click.echo(f"Set camera to: {camera}")
    if film:
        click.echo(f"Set film to:   {film}")
    if iso:
        click.echo(f"Set ISO to:    {iso}")

    click.confirm("Does this look OK?", abort=True)

    workqueue = []
    for f in files:
        p = Path(f)
        if p.exists() and p.is_dir():
            workqueue.extend([x for x in p.glob("*.[jJ][pP][gG]")])
        elif p.exists() and p.is_file():
            workqueue.append(p)

    with click.progressbar(
            workqueue, label="Tagging images...", show_pos=True) as bar:
        for image in bar:
            # Write new metadata to image.
            m = GExiv2.Metadata()
            m.register_xmp_namespace("http://analogexif.sourceforge.net/ns",
                                     "AnalogExif")
            m.open_path(str(image))
            if date:
                m.set_tag_string("Exif.Image.DateTime", exif_datetime)
                m.set_tag_string("Exif.Photo.DateTimeOriginal", exif_datetime)
                m.set_tag_string("Exif.Photo.DateTimeDigitized", exif_datetime)
            if camera:
                if camera not in m.get_tag_multiple("Xmp.dc.subject"):
                    m.set_tag_string("Xmp.dc.subject",
                                     camera)  # set a keyword!
                for k, v in cameras[camera].items():
                    if isinstance(v, int):
                        m.set_tag_long(k, v)
                    else:
                        m.set_tag_string(k, v)
            if film:
                if film not in m.get_tag_multiple("Xmp.dc.subject"):
                    m.set_tag_string("Xmp.dc.subject", film)  # set a keyword!
                m.set_tag_string("Xmp.AnalogExif.Film", film)
                for k, v in films[film].items():
                    if isinstance(v, int):
                        m.set_tag_long(k, v)
                    else:
                        m.set_tag_string(k, v)
            if iso:
                m.set_tag_long("Exif.Photo.ISOSpeedRatings", iso)
            m.save_file(str(image))
    click.echo("Done.")
