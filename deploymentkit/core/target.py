"""Target platform

"""

import os

from deploymentkit.core import backends


def target_list_to_tree(targets):
    """Convert a list of Target instances into a nested dictionary
    with levels family, series, version and arch."""

    def partition(iterable, func):
        result = {}
        for i in iterable:
            result.setdefault(func(i), []).append(i)
        return result

    def get_family(t):
        return t.family

    def get_series(t):
        return t.series

    def get_version(t):
        return t.version

    def get_arch(t):
        return t.architecture

    tree = {}
    for family, targets in partition(targets, get_family).items():
        tree[family] = {}
        for series, targets in partition(targets, get_series).items():
            tree[family][series] = {}
            for version, targets in partition(targets, get_version).items():
                tree[family][series][version] = {}
                for arch, targets in partition(targets, get_arch).items():
                    assert len(targets) == 0, "Duplicate targets found"
                    tree[family][series][version][arch] = targets[0]
    return tree

class TargetIdentifierInterface(object):

    @staticmethod
    def query():
        pass

_target_id_backends = []

def _load_backends():

    _target_id_backends = []

    if not _target_id_backends:
        _target_id_backends = backends.load('TargetIdentifier')

    return _target_id_backends

def get_host():
    """ """

    found_target = None
    for backend in _load_backends():
        target = backend.query()
        if not target:
            pass

        if found_target:
            print 'Warning: Multiple targets identified for host'
        else:
            found_target = target

    return found_target


def get_default():
    """ """

    # TODO: Should maybe be configurable?

    return get_host()


class Target(object):
    """Identifes a target (platform).

    Currently a target must be fully specified. In the future,
    it should be possible to leave some fields blank."""

    # TODO: validate architecture field

    _instance_map = {}

    def __init__(self, identifier_string=None):
        self._family = ''
        self._series = ''
        self._version = ''
        self._architecture = ''

        if identifier_string is not None:
            self.from_string(identifier_string)

    def from_members(self, family, series, version, arch, *ignore):

        self._family = family
        self._series = series
        self._version = version
        self._architecture = arch

    def from_string(self, identifier_string):
        """
        Set the target from a identifier string on form
        Format: family-series-version-architecture
        """

        try:
            family, series, version, arch = identifier_string.split('-')
        except IndexError:
            raise ValueError, 'Invalid target identifier string: %s' % identifier_string
        else:
            self.from_members(family, series, version, arch)

    def to_string(self):
        fields = [self._family, self._series, self._version, self._architecture]
        return '-'.join(fields)

    def __hash__(self):
        return hash(self.to_string())

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return '%s(%s)' % ('Target', self.to_string())

    @property
    def family(self):
        return self._family

    @property
    def series(self):
        return self._series

    @property
    def architecture(self):
        return self._architecture

    @property
    def version(self):
        return self._version


class TargetSpecifier:
    """A target or set of targets can be specified.

    A target identifier is on the form \"$family-$series-$version-$architecture\".
    A set of targets can be specified using a comma separated list of target identifiers.

    Which values are supported for $family, $series, $version and $architecture depends on
    the action to be performed."""

    # TODO: support wildcards

    def __init__(self, specifier_string):
        self._specifier_string = specifier_string

    def get_targets(self, valid_targets=[]):
        """Return the list of targets specified."""

        return [Target(s) for s in self._specifier_string.split(',')]
