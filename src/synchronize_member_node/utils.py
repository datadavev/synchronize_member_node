import datetime

from . import const


def dtToDataONETime(dt: datetime.datetime) -> str:
    dt1 = dt.astimezone(datetime.UTC)
    return dt1.strftime(const.DATAONE_TIME_FORMAT)


def dtnow() -> datetime.datetime:
    """Get datetime for now in UTC timezone."""
    return datetime.datetime.now(datetime.UTC)


def datetimeFromString(v: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(v)
