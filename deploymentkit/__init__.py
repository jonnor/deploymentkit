
from deploymentkit.backends import linux


# FIXME: Register target support dynamically from the backends themselves
# TODO: Use a better way of identifying targets. Should probably incorporate
# at least family, series, version and architecture, and allow for
# more specific fields like version to match against *, <=, == type expressions
# TODO: use a factory function to get targets, given a target identifier

# {Targetid: core.TargetPlatform instance}
supported_targets = {}

supported_targets['ArchLinux'] = linux.Linux('ArchLinux')
supported_targets['OpenSUSE'] = linux.Linux('OpenSUSE')
