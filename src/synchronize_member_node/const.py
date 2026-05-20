import typing

import synchronize_member_node

HTTP_TIMEOUT: float = 20.0
"""HTTP request timeout in seconds."""

DATAONE_TIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

DATAONE_OBJECT_LIST: str = "http://ns.dataone.org/service/types/v1:objectList"

DATAONE_CHECKSUM_ALGORITHMS: typing.Final[tuple[str, str]] = (
    "MD5",
    "SHA-256",
)

HTTP_USER_AGENT: str = f"synchronize_member_node/{synchronize_member_node.__version__}"

JSON_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
"""datetime format string for generating JSON content
"""
