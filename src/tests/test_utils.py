import pytest

from synchronize_member_node import utils


@pytest.mark.parametrize(
    ("input_string", "expected"),
    [
        ("2024-06-01T12:00:00Z", "2024-06-01T12:00:00+00:00"),
        ("2024-06-01T12:00:00+00:00", "2024-06-01T12:00:00+00:00"),
        ("2024-06-01T12:00:00.123456Z", "2024-06-01T12:00:00.123456+00:00"),
    ],
)
def test_datetime_from_string(input_string, expected):
    dt = utils.datetimeFromString(input_string)
    assert dt is not None
    assert dt.isoformat() == expected
