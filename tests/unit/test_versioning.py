from __future__ import annotations

import pytest

from animax.core.versioning import Version, is_compatible, parse


def test_parse_basic() -> None:
    version = parse("1.2.3")
    assert version == Version(major=1, minor=2, patch=3)
    assert str(version) == "1.2.3"


def test_parse_prerelease() -> None:
    version = parse("2.0.0-rc.1")
    assert version.prerelease == "rc.1"
    assert str(version) == "2.0.0-rc.1"


def test_parse_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        parse("not-a-version")


def test_parse_rejects_missing_patch() -> None:
    with pytest.raises(ValueError):
        parse("1.2")


@pytest.mark.parametrize(
    ("required", "actual", "expected"),
    [
        ("1.0.0", "1.5.2", True),
        ("1.0.0", "2.0.0", False),
        ("2.3.1", "2.0.0", True),
        ("1.0.0", "1.0.0", True),
    ],
)
def test_is_compatible(required: str, actual: str, expected: bool) -> None:
    assert is_compatible(required, actual) is expected
