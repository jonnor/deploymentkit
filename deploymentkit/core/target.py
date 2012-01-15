"""Target platform

"""

import os

from deploymentkit.core import backends


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


def targets_from_string(string):
    return [Target(s) for s in string.split(',')]

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

