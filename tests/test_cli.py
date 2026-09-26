"""Tests for the filmtagger CLI."""

import importlib
import os
import tomllib
from importlib.resources import files
from pathlib import Path

import click
import pyexiv2
import pytest
from click.testing import CliRunner

from filmtagger import cli
from filmtagger.cli import main, validate_camera, validate_film

# Click's exit code for a usage error (bad option value).
USAGE_ERROR = 2


def _load(name):
    """Load a packaged TOML database by filename."""
    with files('filmtagger').joinpath(name).open('rb') as f:
        return tomllib.load(f)


# Fixed candidate sets for the fuzzy-match tests. filmtagger.cli merges whatever
# the developer has in ~/.config/filmtagger into its module-level `cameras` and
# `films` globals at import time, so those globals MUST be patched or these
# tests would pass on a machine with a personal config and fail in CI.
TEST_CAMERAS = {'Leica M6': {}, 'Widelux': {}, 'Nikon F100': {}}
TEST_FILMS = {
    'Fuji Acros 100': {},
    'Ilford Delta 100': {},
    'Kodak E100G': {},
    'Kodak Portra 400': {},
    'Kodak Tri-X 400': {},
}


@pytest.fixture
def databases(monkeypatch):
    """Pin the camera/film databases to a known candidate set."""
    monkeypatch.setattr(cli, 'cameras', TEST_CAMERAS)
    monkeypatch.setattr(cli, 'films', TEST_FILMS)


def test_cli_version():
    """Test the --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert 'filmtagger' in result.output


def test_toml_files_load():
    """Test that the TOML files can be loaded successfully."""
    # Test cameras.toml
    cameras = _load('cameras.toml')
    assert isinstance(cameras, dict)
    assert len(cameras) > 0

    # Test films.toml
    films = _load('films.toml')
    assert isinstance(films, dict)
    assert len(films) > 0


# --- Fuzzy matching: normalisation ------------------------------------------


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        # Exact key
        ('Leica M6', 'Leica M6'),
        # Case is ignored
        ('leica m6', 'Leica M6'),
        ('LEICA M6', 'Leica M6'),
        # Punctuation and repeated whitespace are ignored
        ('leica-m6', 'Leica M6'),
        ('  leica   m6  ', 'Leica M6'),
        # Missing separators still match
        ('LeicaM6', 'Leica M6'),
        ('NikonF100', 'Nikon F100'),
        # Extra trailing words are tolerated
        ('Leica M6 TTL', 'Leica M6'),
        # Partial key (substring of the full name)
        ('M6', 'Leica M6'),
        ('f100', 'Nikon F100'),
        # A different camera is not forgiven
        ('Mamiya RB67', None),
    ],
)
@pytest.mark.usefixtures('databases')
def test_validate_camera_matches(value, expected):
    """Test that camera names are fuzzy matched to canonical keys."""
    if expected is None:
        with pytest.raises(click.BadParameter):
            validate_camera(None, None, value)
    else:
        assert validate_camera(None, None, value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('Kodak Portra 400', 'Kodak Portra 400'),
        ('kodak portra 400', 'Kodak Portra 400'),
        ('KODAK PORTRA 400', 'Kodak Portra 400'),
        ('portra-400', 'Kodak Portra 400'),
        ('KodakPortra400', 'Kodak Portra 400'),
        # Substring / partial matches
        ('acros', 'Fuji Acros 100'),
        ('portra', 'Kodak Portra 400'),
        # Hyphenated stock name is matched with or without the hyphen
        ('tri x 400', 'Kodak Tri-X 400'),
        ('tri-x-400', 'Kodak Tri-X 400'),
        # Non-numeric suffix
        ('e100g', 'Kodak E100G'),
        # Not in the database
        ('kodak gold 200', None),
        ('delta 3200', None),
        # 'trix 400' is a plausible typo for 'Tri-X 400' but the words differ,
        # so it is rejected rather than guessed at.
        ('trix 400', None),
    ],
)
@pytest.mark.usefixtures('databases')
def test_validate_film_matches(value, expected):
    """Test that film names are fuzzy matched to canonical keys."""
    if expected is None:
        with pytest.raises(click.BadParameter):
            validate_film(None, None, value)
    else:
        assert validate_film(None, None, value) == expected


# --- Fuzzy matching: a wrong match is worse than no match -------------------


@pytest.mark.parametrize(
    'value',
    [
        # A different camera in the database must not win on similarity alone.
        'Leica M3',
        'M5',
        'Nikon F200',
        'Nikon F3',
    ],
)
@pytest.mark.usefixtures('databases')
def test_camera_model_number_is_never_guessed(value):
    """Test that a wrong camera model is rejected instead of approximated."""
    with pytest.raises(click.BadParameter):
        validate_camera(None, None, value)


@pytest.mark.parametrize(
    'value',
    [
        # A different film speed must not win on similarity alone.
        'Portra 800',
        'Portra 440',
        'Kodak Portra 1600',
        # 'ekta 100' is a typo for 'Ektar 100' but also shares 'ta 100' with
        # 'Ilford Delta 100'; it must match neither.
        'ekta 100',
    ],
)
@pytest.mark.usefixtures('databases')
def test_film_speed_is_never_guessed(value):
    """Test that a wrong film speed is rejected instead of approximated."""
    with pytest.raises(click.BadParameter):
        validate_film(None, None, value)


@pytest.mark.parametrize(
    'value',
    [
        # The real database holds several speeds per film family, so a wrong
        # speed is within one edit of a right one. None may be substituted.
        'Kodak Portra 1600',
        'Kodak Portra 4000',
        'Ilford Delta 320',
        'Ilford Delta 300',
        'Fuji Neopan 100',
        'Fuji Acros 400',
        'Kodak Tri-X 4000',
        'Ilford Delta 1000',
    ],
)
def test_wrong_speed_never_snaps_to_a_neighbouring_speed(monkeypatch, value):
    """Test that a mistyped speed cannot round to a different real speed."""
    monkeypatch.setattr(cli, 'films', _load('films.toml'))
    with pytest.raises(click.BadParameter):
        validate_film(None, None, value)


@pytest.mark.parametrize('value', ['x', 'X', ' ', '  ', 'M', '4'])
@pytest.mark.parametrize('validate', [validate_camera, validate_film])
@pytest.mark.usefixtures('databases')
def test_too_short_to_identify_anything(validate, value):
    """Test that a value with fewer than two characters never matches."""
    with pytest.raises(click.BadParameter):
        validate(None, None, value)


# --- Fuzzy matching: ambiguity ----------------------------------------------


@pytest.mark.parametrize('value', ['ilford delta', 'delta', 'fuji', 'kodak portra'])
def test_ambiguous_film_is_rejected(monkeypatch, value):
    """Test that a value matching several films is rejected, not guessed."""
    monkeypatch.setattr(cli, 'films', _load('films.toml'))
    with pytest.raises(click.BadParameter):
        validate_film(None, None, value)


def test_specific_speed_disambiguates(monkeypatch):
    """Test that adding the film speed resolves an otherwise ambiguous value."""
    monkeypatch.setattr(cli, 'films', _load('films.toml'))
    assert validate_film(None, None, 'ilford delta 3200') == 'Ilford Delta 3200'
    assert validate_film(None, None, 'kodak portra 160') == 'Kodak Portra 160'


# --- Fuzzy matching: edge cases ---------------------------------------------


@pytest.mark.parametrize('validate', [validate_camera, validate_film])
@pytest.mark.usefixtures('databases')
def test_validate_none_passes_through(validate):
    """Test that an omitted option is left untouched."""
    assert validate(None, None, None) is None


@pytest.mark.parametrize('validate', [validate_camera, validate_film])
@pytest.mark.usefixtures('databases')
def test_validate_empty_string_rejected(validate):
    """Test that an empty string is reported as not found, not accepted."""
    with pytest.raises(click.BadParameter):
        validate(None, None, '')


@pytest.mark.parametrize(
    'validate', [validate_camera, validate_film], ids=['camera', 'film']
)
@pytest.mark.usefixtures('databases')
def test_validate_error_message_names_the_database(validate):
    """Test that the failure tells the user which option was wrong."""
    with pytest.raises(click.BadParameter) as excinfo:
        validate(None, None, 'definitely not a real camera or film')
    assert 'not found in database' in str(excinfo.value)


@pytest.mark.usefixtures('databases')
def test_camera_and_film_databases_are_separate():
    """Test that a film name is rejected by --camera and vice versa."""
    with pytest.raises(click.BadParameter):
        validate_camera(None, None, 'Kodak Portra 400')
    with pytest.raises(click.BadParameter):
        validate_film(None, None, 'Leica M6')


# --- Fuzzy matching: the shipped databases ----------------------------------


@pytest.mark.parametrize('name', sorted(_load('cameras.toml')))
def test_every_shipped_camera_round_trips(monkeypatch, name):
    """Test that each cameras.toml key resolves to itself."""
    monkeypatch.setattr(cli, 'cameras', _load('cameras.toml'))
    assert validate_camera(None, None, name) == name


@pytest.mark.parametrize('name', sorted(_load('films.toml')))
def test_every_shipped_film_round_trips(monkeypatch, name):
    """Test that each films.toml key resolves to itself."""
    monkeypatch.setattr(cli, 'films', _load('films.toml'))
    assert validate_film(None, None, name) == name


def test_no_duplicate_keys_in_databases():
    """Test that the shipped databases have no duplicate canonical names."""
    for filename in ('cameras.toml', 'films.toml'):
        keys = list(_load(filename))
        assert len(keys) == len(set(keys)), filename


# --- Fuzzy matching: through the CLI ----------------------------------------


@pytest.mark.usefixtures('databases')
def test_cli_normalises_camera_and_film(tmp_path):
    """Test that --camera/--film are resolved before anything is written."""
    image = tmp_path / 'scan.jpg'
    image.write_bytes(b'')
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['--camera', 'leica-m6', '--film', 'portra 400', str(image)],
        input='n\n',
    )
    assert 'Set camera to: Leica M6' in result.output
    assert 'Set film to:   Kodak Portra 400' in result.output


@pytest.mark.usefixtures('databases')
def test_cli_rejects_unknown_camera(tmp_path):
    """Test that a bad --camera value aborts with a usage error."""
    image = tmp_path / 'scan.jpg'
    image.write_bytes(b'')
    runner = CliRunner()
    result = runner.invoke(main, ['--camera', 'not a camera', str(image)])
    assert result.exit_code == USAGE_ERROR
    assert 'Camera not found in database' in result.output


@pytest.mark.usefixtures('databases')
def test_cli_rejects_unknown_film(tmp_path):
    """Test that a bad --film value aborts with a usage error."""
    image = tmp_path / 'scan.jpg'
    image.write_bytes(b'')
    runner = CliRunner()
    result = runner.invoke(main, ['--film', 'not a film', str(image)])
    assert result.exit_code == USAGE_ERROR
    assert 'Film not found in database' in result.output


# --- User config merging -----------------------------------------------------


@pytest.fixture
def reloaded_cli(monkeypatch, tmp_path):
    """Re-import filmtagger.cli with the user config dir pointed at tmp_path."""
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    module = importlib.reload(cli)
    try:
        yield module, module.CAMERA_CONFIG_FILE.parent
    finally:
        monkeypatch.undo()
        importlib.reload(cli)


def test_config_dir_honours_xdg_config_home(reloaded_cli):
    """Test that user config is read from $XDG_CONFIG_HOME/filmtagger."""
    _, configdir = reloaded_cli
    assert configdir == Path(os.environ['XDG_CONFIG_HOME']) / 'filmtagger'


def test_user_config_is_merged(reloaded_cli):
    """Test that user entries are added to, and override, the shipped ones."""
    module, configdir = reloaded_cli
    configdir.mkdir(parents=True, exist_ok=True)
    configdir.joinpath('cameras.toml').write_text(
        '["Hasselblad 500C/M"]\n"Exif.Image.Make" = "Hasselblad"\n'
        '["Leica M6"]\n"Exif.Image.Model" = "Leica M6 (overridden)"\n'
    )
    configdir.joinpath('films.toml').write_text(
        '["Cinestill 800T"]\n"Exif.Photo.ISOSpeedRatings" = 800\n'
    )
    module = importlib.reload(cli)

    # New entries are available
    assert 'Hasselblad 500C/M' in module.cameras
    assert 'Cinestill 800T' in module.films
    # The shipped entries are all still there
    assert 'Widelux' in module.cameras
    assert 'Kodak Portra 400' in module.films
    # The user entry wins on collision
    assert module.cameras['Leica M6']['Exif.Image.Model'] == 'Leica M6 (overridden)'
    # A user's film list must not leak camera entries into it
    assert 'Hasselblad 500C/M' not in module.films
    # The merged names are still fuzzy matchable
    assert cli.validate_camera(None, None, 'hasselblad 500cm') == 'Hasselblad 500C/M'


def test_invalid_user_config_exits(reloaded_cli):
    """Test that malformed user TOML aborts instead of being silently ignored."""
    _, configdir = reloaded_cli
    configdir.mkdir(parents=True, exist_ok=True)
    configdir.joinpath('cameras.toml').write_text('this is not = = toml')

    with pytest.raises(SystemExit) as excinfo:
        importlib.reload(cli)
    assert excinfo.value.code == 1


def test_pyexiv2_import():
    """Test that pyexiv2 can be imported successfully."""
    # Basic test to ensure the module is available
    assert hasattr(pyexiv2, 'Image')
    assert hasattr(pyexiv2, '__version__')
