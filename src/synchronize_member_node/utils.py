import dataclasses
import datetime
import json
import typing

from . import const


def dtToDataONETime(dt: datetime.datetime) -> str:
    dt1 = dt.astimezone(datetime.UTC)
    return dt1.strftime(const.DATAONE_TIME_FORMAT)


def dtnow() -> datetime.datetime:
    """Get datetime for now in UTC timezone."""
    return datetime.datetime.now(datetime.UTC)


def datetimeFromString(v: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(v)


def datetimeToJsonStr(dt: datetime.datetime | None) -> str | None:
    """Convert datetime to a JSON compatible string"""
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # Naive timestamp, convention is this must be UTC
        return f"{dt.strftime(const.JSON_TIME_FORMAT)}Z"
    return dt.strftime(const.JSON_TIME_FORMAT)


class DataclassJsonEncoder(json.JSONEncoder):
    def default(self, o: typing.Any) -> typing.Any:
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        if isinstance(o, datetime.datetime):
            return datetimeToJsonStr(o)
        return super().default(o)
