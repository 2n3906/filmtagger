import click

import toml
from fuzzywuzzy import process
from pathlib import Path
from dateutil import parser
# import re

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

import pkg_resources

cameras = toml.load(pkg_resources.resource_filename(__name__, "cameras.toml"))
films = toml.load(pkg_resources.resource_filename(__name__, "films.toml"))


def validate_date(ctx, param, value):
    try:
        date = parser.parse(value)
        return date
    except ValueError:
        raise click.BadParameter('Could not parse date "{}"'.format(value))


def validate_camera(ctx, param, value):
    if value is not None:
        match = process.extractOne(value, cameras.keys(), score_cutoff=80)
        if match:
            return match[0]
        else:
            raise click.BadParameter('Camera "{}" not found.'.format(value))
    else:
        return value


def validate_film(ctx, param, value):
    if value is not None:
        match = process.extractOne(value, films.keys(), score_cutoff=80)
        if match:
            return match[0]
        else:
            raise click.BadParameter('Film "{}" not found.'.format(value))
    else:
        return value


@click.command()
@click.option('--camera', '-c', help='Camera name.', callback=validate_camera)
@click.option(
    '--date',
    '-d',
    help='Date of image capture.',
    callback=validate_date,
    required=True)
@click.option('--film', '-f', help='Film name.', callback=validate_film)
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def main(camera, date, film, files):
    """Simple CLI to tag film scans with EXIF metadata."""
    exif_datetime = date.strftime('%Y:%m:%d %H:%M:%S')

    click.echo('Set dates to:  {}'.format(date))
    if camera:
        click.echo('Set camera to: {}'.format(camera))
    if film:
        click.echo('Set film to:   {}'.format(film))

    click.confirm('Does this look OK?', abort=True)

    workqueue = []
    for f in files:
        p = Path(f)
        if p.exists() and p.is_dir():
            workqueue.extend([x for x in p.glob("*.[jJ][pP][gG]")])
        elif p.exists() and p.is_file():
            workqueue.append(p)

    with click.progressbar(
            workqueue, label='Tagging images...', show_pos=True) as bar:
        for image in bar:
            # Write new metadata to image.
            m = GExiv2.Metadata()
            m.register_xmp_namespace("http://analogexif.sourceforge.net/ns",
                                     "AnalogExif")
            m.open_path(str(image))
            m.set_tag_string('Exif.Image.DateTime', exif_datetime)
            m.set_tag_string('Exif.Photo.DateTimeOriginal', exif_datetime)
            m.set_tag_string('Exif.Photo.DateTimeDigitized', exif_datetime)
            if camera:
                if not camera in m.get_tag_multiple('Xmp.dc.subject'):
                    m.set_tag_string('Xmp.dc.subject',
                                     camera)  # set a keyword!
                for k, v in cameras[camera].items():
                    if isinstance(v, int):
                        m.set_tag_long(k, v)
                    else:
                        m.set_tag_string(k, v)
            if film:
                if not film in m.get_tag_multiple('Xmp.dc.subject'):
                    m.set_tag_string('Xmp.dc.subject', film)  # set a keyword!
                m.set_tag_string('Xmp.AnalogExif.Film', film)
                for k, v in films[film].items():
                    if isinstance(v, int):
                        m.set_tag_long(k, v)
                    else:
                        m.set_tag_string(k, v)
            m.save_file(str(image))
    click.echo("Done.")
