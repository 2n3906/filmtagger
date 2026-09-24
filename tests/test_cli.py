"""Tests for the filmtagger CLI."""

from importlib.resources import files

import pyexiv2
import tomli
from click.testing import CliRunner

from filmtagger.cli import main


def test_cli_version():
    """Test the --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert 'filmtagger' in result.output


def test_toml_files_load():
    """Test that the TOML files can be loaded successfully."""
    # Test cameras.toml
    with files('filmtagger').joinpath('cameras.toml').open('rb') as f:
        cameras = tomli.load(f)
    assert isinstance(cameras, dict)
    assert len(cameras) > 0

    # Test films.toml
    with files('filmtagger').joinpath('films.toml').open('rb') as f:
        films = tomli.load(f)
    assert isinstance(films, dict)
    assert len(films) > 0


def test_pyexiv2_import():
    """Test that pyexiv2 can be imported successfully."""
    # Basic test to ensure the module is available
    assert hasattr(pyexiv2, 'Image')
    assert hasattr(pyexiv2, '__version__')
