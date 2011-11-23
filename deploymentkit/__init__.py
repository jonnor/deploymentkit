
from deploymentkit.backends import linux

# {Targetid: core.TargetPlatform instance}
supported_targets = {}

supported_targets['ArchLinux'] = linux.Linux('ArchLinux')
supported_targets['OpenSUSE'] = linux.Linux('OpenSUSE')
