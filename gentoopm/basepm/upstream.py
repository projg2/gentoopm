# (c) 2024 Anna <cyber@sysrq.in>
# SPDX-License-Identifier: GPL-2.0-or-later

import typing
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto


class PMUpstreamMaintainerStatus(Enum):
    """
    Maintainer status enumeration.
    """

    NONE = auto()
    ACTIVE = auto()
    INACTIVE = auto()


@dataclass(frozen=True, order=True)
class PMUpstreamMaintainer:
    """
    Representation of an upstream maintainer.
    """

    name: str
    email: typing.Optional[str] = None
    status: PMUpstreamMaintainerStatus = PMUpstreamMaintainerStatus.NONE

    def __str__(self) -> str:
        if self.name and self.email:
            return f"{self.name} <{self.email}>"
        return self.name


@dataclass(frozen=True)
class PMUpstreamDoc:
    """
    Representation of a link to the upstream documentation.
    """

    url: str
    lang: typing.Optional[str] = None

    def __str__(self) -> str:
        return self.url


@dataclass(frozen=True)
class PMUpstreamRemoteID:
    """
    Representation of an upstream remote-id.
    """

    name: str
    site: str

    def __str__(self) -> str:
        return f"{self.name}: {self.site}"


@dataclass
class PMUpstream:
    """
    Representation of upstream metadata.
    """

    bugs_to: typing.Optional[str] = None
    changelog: typing.Optional[str] = None
    docs: typing.Optional[Iterable[PMUpstreamDoc]] = None
    maintainers: typing.Optional[Iterable[PMUpstreamMaintainer]] = None
    remote_ids: typing.Optional[Iterable[PMUpstreamRemoteID]] = None
