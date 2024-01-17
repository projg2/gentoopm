# (c) 2024 Anna <cyber@sysrq.in>
# SPDX-License-Identifier: GPL-2.0-or-later

import typing
from abc import abstractmethod
from collections.abc import Sequence
from enum import Enum

from ..util import (
    ABCObject,
    StringCompat
)


class PMUpstreamMaintainerStatus(Enum):
    """
    Maintainer status enumeration.
    """

    UNKNOWN = None
    ACTIVE = "active"
    INACTIVE = "inactive"


class PMUpstreamMaintainer(ABCObject, StringCompat):
    """
    A base class for an upstream maintainer.
    """

    _name: str
    _email: typing.Optional[str]
    _status: PMUpstreamMaintainerStatus

    def __new__(cls, name: str, email: typing.Optional[str] = None,
                status: PMUpstreamMaintainerStatus = PMUpstreamMaintainerStatus.UNKNOWN):
        """
        Instantiate the actual string. Requires other props prepared
        beforehand.

        @param email: maintainer's e-mail address
        @param name: maintainer's name
        @param status: maintainer's activity status
        """

        parts = [name]
        if email is not None:
            parts.append(f"<{email}>")

        ret = StringCompat.__new__(cls, " ".join(parts))
        ret._name = name
        ret._email = email
        ret._status = status
        return ret

    @property
    def name(self) -> str:
        """
        Maintainer's name.
        """
        return self._name

    @property
    def email(self) -> typing.Optional[str]:
        """
        Maintainer's e-mail address.
        """
        return self._email

    @property
    def status(self) -> PMUpstreamMaintainerStatus:
        """
        Maintainer's activity status.
        """
        return self._status


class PMUpstreamDoc(ABCObject, StringCompat):
    """
    A base class for a link to the upstream documentation.
    """

    _url: str
    _lang: str

    def __new__(cls, url: str, lang: str = "en"):
        """
        Instantiate the actual string. Requires other props prepared
        beforehand.

        @param url: documentation URL
        @param lang: documentation language
        """

        ret = StringCompat.__new__(cls, url)
        ret._url = url
        ret._lang = lang
        return ret

    @property
    def url(self) -> str:
        """
        Documentation URL.
        """
        return self._url

    @property
    def lang(self) -> str:
        """
        Documentation language.
        """
        return self._lang


class PMUpstreamRemoteID(ABCObject, StringCompat):
    """
    A base class for an upstream remote-id.
    """

    _name: str
    _site: str

    def __new__(cls, name: str, site: str):
        """
        Instantiate the actual string. Requires other props prepared
        beforehand.

        @param name: package's identifier on the site
        @param site: type of package identification tracker
        """

        ret = StringCompat.__new__(cls, f"{site}: {name}")
        ret._name = name
        ret._site = site
        return ret

    @property
    def name(self) -> str:
        """
        Package's identifier on the site.
        """
        return self._name

    @property
    def site(self) -> str:
        """
        Type of package identification tracker.
        """
        return self._site


class PMUpstream(ABCObject):
    """
    An abstract class representing upstream metadata.
    """

    @property
    def bugs_to(self) -> typing.Optional[str]:
        """
        Location where to report bugs (may also be an email address prefixed
        with "mailto:").
        """
        raise NotImplementedError

    @property
    def changelog(self) -> typing.Optional[str]:
        """
        URL where the upstream changelog can be found.
        """
        raise NotImplementedError

    @property
    def docs(self) -> Sequence[PMUpstreamDoc]:
        """
        URLs where the location of the upstream documentation can be found.
        """
        raise NotImplementedError

    @property
    def maintainers(self) -> Sequence[PMUpstreamMaintainer]:
        """
        Upstream maintainers.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def remote_ids(self) -> Sequence[PMUpstreamRemoteID]:
        """
        Package's identifiers on third-party trackers.
        """
