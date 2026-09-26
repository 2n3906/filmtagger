import os
import sys
import tomllib
from importlib.resources import files
from pathlib import Path

import click
import pyexiv2
from dateutil import parser
from rapidfuzz import process, fuzz, utils

# Register the AnalogExif XMP namespace globally
pyexiv2.registerNs('http://analogexif.sourceforge.net/ns/', 'AnalogExif')

# Load system-wide camera & film definitions
with files(__package__).joinpath('cameras.toml').open('rb') as f:
    cameras = tomllib.load(f)
with files(__package__).joinpath('films.toml').open('rb') as f:
    films = tomllib.load(f)

# Load user-provided camera & film definitions and merge
# Config files should be stored in:
#     (UNIX)  ~/.config/filmtagger/*.toml
#     (Win32) C:\Users\username\AppData\Roaming\filmtagger\*.toml
if sys.platform == 'win32':
    CAMERA_CONFIG_FILE = Path(os.environ.get('APPDATA')) / 'filmtagger' / 'cameras.toml'
    FILM_CONFIG_FILE = Path(os.environ.get('APPDATA')) / 'filmtagger' / 'films.toml'
else:
    configpath = Path(os.environ.get('HOME')) / '.config'
    if os.environ.get('XDG_CONFIG_HOME'):
        configpath = Path(os.environ.get('XDG_CONFIG_HOME'))
    CAMERA_CONFIG_FILE = configpath / 'filmtagger' / 'cameras.toml'
    FILM_CONFIG_FILE = configpath / 'filmtagger' / 'films.toml'

if Path(CAMERA_CONFIG_FILE).is_file():
    try:
        with open(CAMERA_CONFIG_FILE, 'rb') as f:
            user_cameras = tomllib.load(f)
        cameras = {**cameras, **user_cameras}
    except tomllib.TOMLDecodeError:
        click.echo(f'File {CAMERA_CONFIG_FILE} is not valid TOML.', err=True)
        sys.exit(1)
if Path(FILM_CONFIG_FILE).is_file():
    try:
        with open(FILM_CONFIG_FILE, 'rb') as f:
            user_films = tomllib.load(f)
        films = {**films, **user_films}
    except tomllib.TOMLDecodeError:
        click.echo(f'File {FILM_CONFIG_FILE} is not valid TOML.', err=True)
        sys.exit(1)


def validate_date(_ctx, _param, value):
    if value is not None:
        try:
            return parser.parse(value)
        except ValueError:
            msg = 'Could not parse date.'
            raise click.BadParameter(msg) from None
    return value


def validate_camera(_ctx, _param, value):
    if value is not None:
        match = process.extractOne(
            value,
            cameras.keys(),
            scorer=fuzz.partial_ratio,
            processor=utils.default_process,
            score_cutoff=85,
        )
        if match:
            return match[0]
        msg = 'Camera not found in database.'
        raise click.BadParameter(msg)
    return value


def validate_film(_ctx, _param, value):
    if value is not None:
        match = process.extractOne(
            value,
            films.keys(),
            scorer=fuzz.partial_ratio,
            processor=utils.default_process,
            score_cutoff=85,
        )
        if match:
            return match[0]
        msg = 'Film not found in database.'
        raise click.BadParameter(msg)
    return value


def collect_files(paths):
    """Expand CLI file/directory arguments into a flat list of files."""
    workqueue = []
    for path in paths:
        p = Path(path)
        if p.is_dir():
            workqueue.extend(p.glob('*.[jJ][pP][gG]'))
        elif p.is_file():
            workqueue.append(p)
    return workqueue


def tag_image(image, camera, film, date, iso, exif_datetime):
    """Write camera, film, date, and ISO metadata to a single image."""
    with pyexiv2.Image(str(image)) as img:
        exif_data = {}
        xmp_data = {}

        # Get existing XMP data once to handle keywords properly
        try:
            existing_xmp = img.read_xmp()
        except Exception:
            existing_xmp = {}

        # Handle keywords/subjects
        existing_subjects = []
        if 'Xmp.dc.subject' in existing_xmp:
            subject_value = existing_xmp['Xmp.dc.subject']
            if isinstance(subject_value, str):
                existing_subjects = [
                    s.strip() for s in subject_value.split(';') if s.strip()
                ]
            elif isinstance(subject_value, list):
                existing_subjects = [
                    str(s).strip() for s in subject_value if str(s).strip()
                ]

        # Add new subjects
        new_subjects = existing_subjects.copy()
        if camera and camera not in new_subjects:
            new_subjects.append(camera)
        if film and film not in new_subjects:
            new_subjects.append(film)

        # Set date metadata
        if date:
            exif_data['Exif.Image.DateTime'] = exif_datetime
            exif_data['Exif.Photo.DateTimeOriginal'] = exif_datetime
            exif_data['Exif.Photo.DateTimeDigitized'] = exif_datetime

        # Set camera metadata
        if camera:
            for key, val in cameras[camera].items():
                if key.startswith('Exif.'):
                    exif_data[key] = str(val)
                elif key.startswith('Xmp.'):
                    xmp_data[key] = str(val)

        # Set film metadata
        if film:
            xmp_data['Xmp.AnalogExif.Film'] = film
            for key, val in films[film].items():
                if key.startswith('Exif.'):
                    exif_data[key] = str(val)
                elif key.startswith('Xmp.'):
                    xmp_data[key] = str(val)

        # Set ISO metadata
        if iso:
            exif_data['Exif.Photo.ISOSpeedRatings'] = str(iso)

        # Set subjects/keywords
        if new_subjects != existing_subjects:
            xmp_data['Xmp.dc.subject'] = ';'.join(new_subjects)

        # Apply metadata changes
        if exif_data:
            img.modify_exif(exif_data)
        if xmp_data:
            img.modify_xmp(xmp_data)


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(package_name='filmtagger', prog_name='filmtagger')
@click.option('--date', '-d', help='Date of image capture.', callback=validate_date)
@click.option('--camera', '-c', help='Camera name.', callback=validate_camera)
@click.option('--film', '-f', help='Film name.', callback=validate_film)
@click.option(
    '--iso', '-i', help='ISO rating (overrides film definition)', type=click.INT
)
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
def main(camera, date, film, iso, files):
    """Tag scanned images with film-specific EXIF metadata."""

    exif_datetime = date.strftime('%Y:%m:%d %H:%M:%S') if date else None
    if date:
        click.echo(f'Set dates to:  {date}')
    if camera:
        click.echo(f'Set camera to: {camera}')
    if film:
        click.echo(f'Set film to:   {film}')
    if iso:
        click.echo(f'Set ISO to:    {iso}')

    click.confirm('Does this look OK?', abort=True)

    workqueue = collect_files(files)
    with click.progressbar(workqueue, label='Tagging images...', show_pos=True) as bar:
        for image in bar:
            tag_image(image, camera, film, date, iso, exif_datetime)
    click.echo('Done.')
