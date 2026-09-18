import pytest
from pydantic import ValidationError

from schema import validate_manifest


def _entry(**overrides):
    return {
        "name": "Test App",
        "owner": "aiven-labs",
        "repo": "test-app",
        "added": "2026-09-18",
        **overrides,
    }


def test_valid_entry_round_trips():
    [result] = validate_manifest([_entry()])
    assert result["added"] == "2026-09-18"


def test_missing_added_fails():
    entry = _entry()
    del entry["added"]
    with pytest.raises(ValidationError, match="added"):
        validate_manifest([entry])


def test_unknown_field_fails():
    with pytest.raises(ValidationError, match="discription"):
        validate_manifest([_entry(discription="typo'd key")])
