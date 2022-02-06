========
gentoopm
========

GentooPM is a wrapper for API of Gentoo package managers (Portage_,
PkgCore_ and historically Paludis_).  It has historically served two
purposes:

1. Making it possible to easily write apps that can utilize any
   of the available PMs.

2. Replacing the awful API provided by package managers (especially
   Portage) with something more Pythonic, easier to use and more
   readable.

The project provides a ``gentoopmq`` tool providing basic lookups
into the PM data.  Most importantly, it provides an IPython-friendly
``gentoopmq shell`` command that can be used to play with the API.

The project is currently in keep-alive mode.  It is updated to keep
existing consumers working but no new features are implemented.  Paludis
support is no longer tested and is behind other PMs, primarily because
Paludis is no longer maintaining Gentoo ebuild support and has not been
updated to support new EAPIs at the time of writing.

The author's recommendation is to use PkgCore_ directly.


.. _Portage: https://wiki.gentoo.org/wiki/Project:Portage
.. _PkgCore: https://github.com/pkgcore/pkgcore
.. _Paludis: https://paludis.exherbo.org/
