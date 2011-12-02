"""Target platform

"""

import os

def get_host():
    """ """

    # FIXME: Come up with a generic way of fetching this
    # Same pattern as for generator backends?
    from deploymentkit.backends import archlinux
    return archlinux.get_host()

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
