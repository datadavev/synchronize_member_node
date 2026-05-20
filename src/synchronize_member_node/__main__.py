"""CLI for synchronize_member_node."""

import logging

import click
import dateparser

from . import const, objectlist


def get_logger() -> logging.Logger:
    return logging.getLogger("syncmn")


@click.group()
@click.option("--log-level", default="INFO", help="Set the logging level (INFO)")
def main(log_level: str) -> int:
    logger = get_logger()
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        msg = f"Invalid log level: {log_level}"
        raise ValueError(msg)
    logging.basicConfig(level=numeric_level)
    logger.setLevel(numeric_level)
    return 0


@main.command(name="objects")
@click.argument("mn_url")
@click.option(
    "-f",
    "--from-date",
    default=None,
    help="Limit to entries with dateSysMetadatModified >= from-date.",
)
@click.option(
    "-t",
    "--to-date",
    default=None,
    help="Limit to entries with dateSysMetadatModified < to-date.",
)
@click.option(
    "-d", "--formatid", default=None, help="Restrict to entries with matching formatId."
)
@click.option(
    "-i", "--identifier", default=None, help="Restrict to specified identifier."
)
@click.option(
    "--no-replicas",
    is_flag=True,
    help="Do not return entries that have any entry in SystemMetadata.replicated.",
)
@click.option(
    "-s",
    "--start",
    "start_offset",
    default=0,
    help="Zero based offset of first entry.",
)
@click.option(
    "-c",
    "--count",
    "max_entries",
    type=int,
    default=10,
    help="Maximum number of entries to retrieve.",
)
@click.option(
    "--timeout",
    type=float,
    default=const.HTTP_TIMEOUT,
    help="HTTP request timeout in seconds.",
)
@click.option(
    "--page-size",
    type=int,
    default=1000,
    help="Number of records to retrieve per request",
)
def list_objects(
    mn_url: str,
    from_date: str | None,
    to_date: str | None,
    formatid: str | None,
    identifier: str | None,
    no_replicas: bool,
    start_offset: int,
    max_entries: int,
    timeout: float,
    page_size: int,
) -> None:
    """Perform a listObjects operation on the specified listObjects endpoint URL.

    Note that the full listObjects URL must be specified, not the MN base url.
    """
    from_datedt = None
    to_datedt = None
    if from_date is not None:
        from_datedt = dateparser.parse(from_date)
    if to_date is not None:
        to_datedt = dateparser.parse(to_date)
    page_size = int(page_size)
    timeout = float(timeout)
    with objectlist.ObjectList(
        mn_url,
        formatid=formatid,
        identifier=identifier,
        replica_status=no_replicas,
        from_date=from_datedt,
        to_date=to_datedt,
        offset=start_offset,
        max_entries=max_entries,
        page_size=page_size,
        timeout=timeout,
    ) as ol:
        print(f"Total entries = {len(ol)}")
        for info in ol:
            print(info)


if __name__ == "__main__":
    main()
