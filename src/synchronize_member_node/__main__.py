"""CLI for synchronize_member_node."""

import logging

import click

from . import objectlist


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
    "-x", "--max", "max_entries", type=int, default=10, help="Max entries to retrieve."
)
def list_objects(mn_url: str, max_entries: int) -> None:
    with objectlist.ObjectList(mn_url, max_entries=max_entries) as ol:
        for info in ol:
            print(info)


if __name__ == "__main__":
    main()
