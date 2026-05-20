import dataclasses
import datetime
import json
import logging
import types

import httpx
import xmltodict

from . import const, utils


def get_logger() -> logging.Logger:
    return logging.getLogger("objectlist")


@dataclasses.dataclass(slots=True)
class ObjectInfo:
    identifier: str
    formatId: str
    checksum_algorithm: str
    checksum: str
    dateSysMetadataModified: datetime.datetime
    size: int

    def __post_init__(self) -> None:
        assert len(self.identifier) > 0
        assert " " not in self.identifier
        assert self.size >= 0

    def __repr__(self) -> str:
        return json.dumps(self, cls=utils.DataclassJsonEncoder)


class ObjectList:
    """Implements a pager for the getObjects() DataONE API."""

    def __init__(
        self,
        lo_url: str,
        formatid: str | None = None,
        identifier: str | None = None,
        replica_status: bool = True,
        offset: int = 0,
        max_entries: int = -1,
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
        page_size: int = 1000,
        timeout: float = const.HTTP_TIMEOUT,
    ):
        self._url = lo_url
        self._formatid = formatid
        self._identifier = identifier
        self._replica_status = replica_status
        self._start_offset = offset
        self._max_entries = max_entries
        self._page_size = page_size
        if self._max_entries > 0 and self._max_entries < self._page_size:
            self._page_size = self._max_entries
        self._from_date = from_date
        self._to_date = to_date
        self._cpage: None | list[ObjectInfo] = None  # current page buffer
        self._coffset = self._start_offset  # offset in MN "list"
        self._page_offset = 0  # offset within a page
        self._total_records = 0  # total records on MN
        self._started = False
        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Accept": "text/xml,application/xml",
                "User-Agent": const.HTTP_USER_AGENT,
            },
        )

    def __enter__(self) -> "ObjectList":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType,
    ) -> None:
        self._client.close()

    def __iter__(self) -> "ObjectList":
        return self

    def __len__(self) -> int:
        if self._cpage is None:
            self._getPage()
        return self._total_records

    def __next__(self) -> ObjectInfo:
        _L = get_logger()
        if not self._started:
            _L.debug("Starting object iteration")
            self._getPage()
            self._started = True
        if self._cpage is None or len(self._cpage) == 0:
            _L.debug("Out of pages")
            raise StopIteration
        if self._max_entries > 0 and self._coffset >= self._max_entries:
            _L.debug("Exceeding max entries, stopping")
            raise StopIteration
        if self._page_offset >= len(self._cpage):
            self._getPage()
        try:
            entry = self._cpage[self._page_offset]
            self._page_offset += 1
            self._coffset += 1
            return entry
        except IndexError as e:
            _L.warning("Stop from %s", e)
        except KeyError as e:
            _L.warning("Stop from %s", e)
        except TypeError as e:
            _L.warning("Stop from %s", e)
        except ValueError as e:
            _L.warning("Stop from %s", e)
        raise StopIteration

    def _getPage(self) -> None:
        _L = get_logger()
        params: dict[str, int | str] = {
            "start": self._coffset,
            "count": self._page_size,
        }
        if self._from_date is not None:
            params["fromDate"] = utils.dtToDataONETime(self._from_date)
        if self._to_date is not None:
            params["toDate"] = utils.dtToDataONETime(self._to_date)
        if self._formatid is not None:
            params["formatId"] = self._formatid
        if self._identifier is not None:
            params["identifier"] = self._identifier
        if self._replica_status:
            params["replicaStatus"] = "false"
        _L.debug("request params: %s", params)
        response = self._client.get(self._url, params=params)
        response.raise_for_status()
        olist = xmltodict.parse(response.text, process_namespaces=True)
        self._total_records = int(olist[const.DATAONE_OBJECT_LIST]["@total"])
        self._cpage = []
        for entry in olist[const.DATAONE_OBJECT_LIST].get("objectInfo", []):
            try:
                r = ObjectInfo(
                    identifier=entry["identifier"],
                    formatId=entry["formatId"],
                    checksum_algorithm=entry["checksum"]["@algorithm"],
                    checksum=entry["checksum"]["#text"],
                    dateSysMetadataModified=utils.datetimeFromString(
                        entry["dateSysMetadataModified"]
                    ),
                    size=int(entry["size"]),
                )
                self._cpage.append(r)
            except Exception as e:
                _L.error("ERROR converting record: %s", e)
        self._page_offset = 0
