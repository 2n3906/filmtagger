"""Tests for the filmtagger CLI."""
import pytest
from click.testing import CliRunner
from filmtagger.cli import main

def test_cli_version():
    """Test the --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "filmtagger" in result.output 