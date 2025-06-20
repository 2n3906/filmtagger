"""Tests for the filmtagger CLI."""

import pytest
import tomli
import importlib.resources
from click.testing import CliRunner
from filmtagger.cli import main


def test_cli_version():
    """Test the --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "filmtagger" in result.output


def test_toml_files_load():
    """Test that the TOML files can be loaded successfully."""
    # Test cameras.toml
    with importlib.resources.open_binary("filmtagger", "cameras.toml") as f:
        cameras = tomli.load(f)
    assert isinstance(cameras, dict)
    assert len(cameras) > 0

    # Test films.toml
    with importlib.resources.open_binary("filmtagger", "films.toml") as f:
        films = tomli.load(f)
    assert isinstance(films, dict)
    assert len(films) > 0
