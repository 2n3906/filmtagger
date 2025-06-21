from .__about__ import __version__
import importlib.resources
import os
import sys
from pathlib import Path

import click

# import re
import pyexiv2
import tomli
from dateutil import parser
from fuzzywuzzy import process

# Load system-wide camera & film definitions
with importlib.resources.open_binary(__name__, "cameras.toml") as f:
    cameras = tomli.load(f)
with importlib.resources.open_binary(__name__, "films.toml") as f:
    films = tomli.load(f)

# Load user-provided camera & film definitions and merge
# Config files should be stored in:
#     (UNIX)  ~/.config/filmtagger/*.toml
#     (Win32) C:\Users\username\AppData\Roaming\filmtagger\*.toml
if sys.platform == "win32":
    CAMERA_CONFIG_FILE = Path(os.environ.get("APPDATA")) / "filmtagger" / "cameras.toml"
    FILM_CONFIG_FILE = Path(os.environ.get("APPDATA")) / "filmtagger" / "films.toml"
else:
    configpath = Path(os.environ.get("HOME")) / ".config"
    if os.environ.get("XDG_CONFIG_HOME"):
        configpath = Path(os.environ.get("XDG_CONFIG_HOME"))
    CAMERA_CONFIG_FILE = configpath / "filmtagger" / "cameras.toml"
    FILM_CONFIG_FILE = configpath / "filmtagger" / "films.toml"

if Path(CAMERA_CONFIG_FILE).is_file():
    try:
        with open(CAMERA_CONFIG_FILE, "rb") as f:
            user_cameras = tomli.load(f)
        cameras = {**cameras, **user_cameras}
    except tomli.TOMLDecodeError:
        print(f"File {CAMERA_CONFIG_FILE} is not valid TOML.")
        sys.exit(1)
if Path(FILM_CONFIG_FILE).is_file():
    try:
        with open(FILM_CONFIG_FILE, "rb") as f:
            user_films = tomli.load(f)
        films = {**cameras, **user_films}
    except tomli.TOMLDecodeError:
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
@click.version_option(__version__, prog_name="filmtagger")
@click.option("--date", "-d", help="Date of image capture.", callback=validate_date)
@click.option("--camera", "-c", help="Camera name.", callback=validate_camera)
@click.option("--film", "-f", help="Film name.", callback=validate_film)
@click.option("--iso", "-i", help="ISO rating (overrides film definition)", type=click.INT)
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

    with click.progressbar(workqueue, label="Tagging images...", show_pos=True) as bar:
        for image in bar:
            # Write new metadata to image.
            with pyexiv2.Image(str(image)) as img:
                # Register the AnalogExif XMP namespace
                pyexiv2.registerNs("http://analogexif.sourceforge.net/ns/", "AnalogExif")
                
                # Prepare metadata dictionaries
                exif_data = {}
                xmp_data = {}
                
                # Get existing XMP data once to handle keywords properly
                try:
                    existing_xmp = img.read_xmp()
                except Exception:
                    existing_xmp = {}
                
                # Handle keywords/subjects
                existing_subjects = []
                if "Xmp.dc.subject" in existing_xmp:
                    subject_value = existing_xmp["Xmp.dc.subject"]
                    if isinstance(subject_value, str):
                        existing_subjects = [s.strip() for s in subject_value.split(";") if s.strip()]
                    elif isinstance(subject_value, list):
                        existing_subjects = [str(s).strip() for s in subject_value if str(s).strip()]
                
                # Add new subjects
                new_subjects = existing_subjects.copy()
                if camera and camera not in new_subjects:
                    new_subjects.append(camera)
                if film and film not in new_subjects:
                    new_subjects.append(film)
                
                # Set date metadata
                if date:
                    exif_data["Exif.Image.DateTime"] = exif_datetime
                    exif_data["Exif.Photo.DateTimeOriginal"] = exif_datetime
                    exif_data["Exif.Photo.DateTimeDigitized"] = exif_datetime
                
                # Set camera metadata
                if camera:
                    for k, v in cameras[camera].items():
                        if k.startswith("Exif."):
                            exif_data[k] = str(v)
                        elif k.startswith("Xmp."):
                            xmp_data[k] = str(v)
                
                # Set film metadata
                if film:
                    xmp_data["Xmp.AnalogExif.Film"] = film
                    for k, v in films[film].items():
                        if k.startswith("Exif."):
                            exif_data[k] = str(v)
                        elif k.startswith("Xmp."):
                            xmp_data[k] = str(v)
                
                # Set ISO metadata
                if iso:
                    exif_data["Exif.Photo.ISOSpeedRatings"] = str(iso)
                
                # Set subjects/keywords
                if new_subjects != existing_subjects:
                    xmp_data["Xmp.dc.subject"] = ";".join(new_subjects)
                
                # Apply metadata changes
                if exif_data:
                    img.modify_exif(exif_data)
                if xmp_data:
                    img.modify_xmp(xmp_data)
    click.echo("Done.")
