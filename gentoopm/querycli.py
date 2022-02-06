#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2017-2022 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import argparse
import os.path
import sys
from abc import abstractmethod

from . import __version__, get_package_manager
from .exceptions import (
    AmbiguousPackageSetError,
    EmptyPackageSetError,
    InvalidAtomStringError,
)
from .submodules import _supported_pms, get_pm
from .util import ABCObject


def _reponame(val):
    """
    Check the value for correctness as repository name. In fact, it only ensures
    it isn't a path so that it won't confuse pm.repositories[val].

    @param val: the config option value
    @type val: string
    @return: whether the value is a correct repo name
    @rtype: bool
    """
    if os.path.isabs(val):
        raise ValueError("Invalid repository name: %s" % val)
    return val


def AtomFormatDict(a):
    return {
        "key": a.key,
        "path": a.path,
        "repository": a.repository,
        "slot": a.slot,
        "subslot": a.subslot,
        "version": a.version,
        "slotted_atom": a.slotted_atom,
        "versioned_atom": a,
        "unversioned_atom": a.unversioned_atom,
    }


class PMQueryCommand(ABCObject):
    """A single gentoopmq command."""

    @classmethod
    def help(self):
        """
        Return the help string for a sub-command.

        @return: the help string
        @rtype: string
        """
        descdoc = " ".join(self.__doc__.split())
        descdoc = descdoc[0].lower() + descdoc[1:]
        return descdoc.rstrip(".")

    def __init__(self, argparser):
        """
        Instantiate the subcommand, setting argument parser as necessary.

        @param argparser: sub-command argument parser
        @type argparser: C{argparse.ArgumentParser}
        """
        argparser.set_defaults(instance=self)
        self._arg = argparser

    @abstractmethod
    def __call__(self, pm, args):
        """
        Call the sub-command, passing pm (a working PackageManager instance)
        and args (the result of argument parsing). Can return exit code
        for the process if relevant. If it doesn't, 0 will be used.

        @param pm: package manager instance
        @type pm: L{PackageManager}
        @param args: command arguments
        @type args: C{argparse.Namespace}
        @return: Process exit code or None if irrelevant
        @rtype: bool/None
        """
        pass


class PMQueryCommands(object):
    """The container of all standard gentoopmq commands."""

    # === generic information ===

    class package_manager(PMQueryCommand):
        """
        Get the name of a working, preferred PM.
        """

        def __init__(self, argparser):
            PMQueryCommand.__init__(self, argparser)
            argparser.add_argument(
                "-v",
                "--with-version",
                action="store_true",
                dest="version",
                help="Print the version as well",
            )

        def __call__(self, pm, args):
            if args.version:
                print("%s %s" % (pm.name, pm.version))
            else:
                print(pm.name)

    # === repository info ===

    class repositories(PMQueryCommand):
        """
        Print the list of ebuild repositories.
        """

        def __call__(self, pm, args):
            print(" ".join([r.name for r in pm.repositories]))

    class repo_path(PMQueryCommand):
        """
        Print the path to the named repository.
        """

        def __init__(self, argparser):
            PMQueryCommand.__init__(self, argparser)
            argparser.add_argument(
                "repo_name", type=_reponame, help="The repository name to look up"
            )

        def __call__(self, pm, args):
            try:
                r = pm.repositories[args.repo_name]
            except KeyError:
                self._arg.error("No repository named %s" % args.repo_name)
                return 1
            print(r.path)

    # === package matching ===

    class match(PMQueryCommand):
        """
        Print packages matching the specified atom.
        """

        def __init__(self, argparser):
            PMQueryCommand.__init__(self, argparser)
            argparser.add_argument(
                "-b", "--best", action="store_true", help="Print only the best version"
            )
            argparser.add_argument(
                "-s",
                "--best-in-slot",
                action="store_true",
                help="Print the best version in each available slot",
            )
            argparser.add_argument(
                "-f",
                "--format",
                default="{versioned_atom}",
                help=(
                    "Output format string (can include: "
                    + "{versioned_atom}, {unversioned_atom}, {slotted_atom}, "
                    + "{key}, {key.category}, {key.package}, "
                    + "{version}, {version.revision}, {version.without_revision}, "
                    + "{slot}, {subslot}, {repository}, {path})"
                ),
            )
            argparser.add_argument(
                "package_atom", nargs="+", help="The package atom to match"
            )

        def __call__(self, pm, args):
            if args.best and args.best_in_slot:
                self._arg.error("--best and --best-in-slot are mutually exclusive")

            for in_atom in args.package_atom:
                try:
                    a = pm.Atom(in_atom)
                except InvalidAtomStringError as e:
                    self._arg.error(e)
                    return 1

                pkgs = pm.stack.filter(a)
                if args.best_in_slot:
                    pkgs = [pg.best for pg in pkgs.group_by("slotted_atom")]
                if args.best:
                    try:
                        pkgs = (pkgs.best,)
                    except AmbiguousPackageSetError:
                        self._arg.error("Multiple disjoint packages match %s" % in_atom)
                        return 1
                    except EmptyPackageSetError:
                        self._arg.error("No packages match %s" % in_atom)
                        return 1
                for p in pkgs:
                    print(args.format.format(**AtomFormatDict(p)))

    # === shell ===

    class shell(PMQueryCommand):
        """
        Run a Python shell with current PM selected.
        """

        def __call__(self, pm, args):
            import gentoopm.filters as f
            import gentoopm.matchers as m

            our_imports = (("pm", pm), ("f", f), ("m", m))

            welc = """The following objects have been imported for you:\n"""
            welc += "\n".join(
                ["\t%s: %s" % (key, repr(var)) for key, var in our_imports]
            )
            kwargs = {}

            try:
                from IPython import embed
            except ImportError:
                try:
                    from IPython.Shell import IPShellEmbed
                except ImportError:
                    print("For better user experience, install IPython.")
                    from code import InteractiveConsole

                    embed = InteractiveConsole({"pm": pm}).interact
                    kwargs["banner"] = welc
                else:
                    embed = IPShellEmbed()
                    embed.set_banner(embed.IP.BANNER + "\n\n" + welc)
            else:
                kwargs["banner2"] = welc

            embed(**kwargs)

    def __iter__(self):
        for k in dir(self):
            if k.startswith("_"):
                continue
            cls = getattr(self, k)
            yield (k.replace("_", "-"), cls.help(), cls)


class PMQueryCLI(object):
    """A CLI for gentoopmq."""

    def __init__(self):
        self.argparser = arg = argparse.ArgumentParser()
        all_pms = frozenset(_supported_pms)

        arg.add_argument(
            "-V",
            "--version",
            action="version",
            version="%s %s" % (arg.prog, __version__),
        )
        arg.add_argument(
            "-p",
            "--package-manager",
            action="store",
            help="Use a specific package manager",
            choices=all_pms,
        )

        subp = arg.add_subparsers(title="Sub-commands")
        for cmd_name, cmd_help, cmd_class in PMQueryCommands():
            p = subp.add_parser(cmd_name, help=cmd_help)
            cmd_class(p)

    def main(self, argv):
        arg = self.argparser
        arg.prog = os.path.basename(argv[0])
        args = arg.parse_args(argv[1:])

        if args.package_manager is not None:
            pm = get_pm(args.package_manager)
        else:
            try:
                pm = get_package_manager()
            except Exception:
                arg.error("No working package manager could be found.")

        return args.instance(pm, args) or 0


def main():
    cli = PMQueryCLI()
    sys.exit(cli.main(sys.argv))
