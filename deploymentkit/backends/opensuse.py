
import os, subprocess

from deploymentkit.core import recipe, target
from deploymentkit.backends import linux, pkgkit, rpm

# FIXME: also support SUSE

opensuse_versions = ['11.2', '11.3', '11.4', '12.1']
opensuse_arctectures = ['i586', 'x86_64']
opensuse_series = 'opensuse'
opensuse_family = 'gnulinux'

opensuse_native_buildtoolchain = 'opensuse-native'

opensuse_supported_targets = []
for version in opensuse_versions:
    for arch in opensuse_arctectures:
        t = target.Target("%s-%s-%s-%s" % (opensuse_family, opensuse_series, version, arch))
        opensuse_supported_targets.append(t)

def is_opensuse(target):

    return (target.family == opensuse_family and target.series == opensuse_series)

class TargetIdentifier(object):

    @staticmethod
    def query():

        # XXX: This is as unreliable/ambigious as detecting a Linux
        # distribution typically is.

        (sysname, nodename, release, version, machine) = os.uname()

        if sysname != 'Linux':
            return None

        if machine == 'i686':
            arch = 'i586' # Somehow that is the official arch name
        else:
            # FIXME: take ARM et.c into account
            arch = 'x86_64'

        release_file = '/etc/SuSE-release'
        if not os.path.exists(release_file):
            return None

        release = open(release_file).read()

        # Typical output
        """openSUSE 11.4 (i586)
        VERSION = 11.4
        CODENAME = Celadon"""

        version = None
        for line in release.split('\n'):
            if line.strip().startswith('VERSION'):
                version = line.split('=')[1].strip()

        t = target.Target()
        t.from_members(opensuse_family, opensuse_series, version, arch)
        return t

class GeneratorBackend(object):

    supported_targets = opensuse_supported_targets

    supported_buildsystems = [
        'autotools',
    ]

    def __init__(self):
        pass

    def generate_build_recipe(self, generic_recipe, targets):

        assert set(targets).intersection(set(self.supported_targets))

        # Map target independent values into target specific values.
        target_pkg_recipe = generic_to_specific_recipe(generic_recipe.data)

        # Create the target specific recipe
        try:
            files = rpm.generate_recipe(target_pkg_recipe)
        except KeyError:
            files = {}

        output = recipe.BuildRecipe()
        output.files = files.keys()
        output.targets = targets
        output.file_contents = files
        output.toolchain = opensuse_native_buildtoolchain

        return output


class BuilderBackend(object):

    supported_targets = opensuse_supported_targets
    toolchain = opensuse_native_buildtoolchain

    def run(self, build_recipe, targets):
        """ """
        
        spec_file = [path for path in build_recipe.files if path.endswith('.spec')][0]
        
        for target in targets:
            # FIXME: need to pass in specified targets properly
            
            if not is_opensuse(target):
                raise ValueError, 'Unsupported target: %s' % target

            cmd = ['sudo', 'build', spec_file]
            print 'INFO: Running command %s' % ' '.join(cmd)
            subprocess.call(cmd)

def generic_to_specific_recipe(generic_data):
    """Return a mapping representing the target specific recipe data
    based on the @generic_data"""

    # XXX: perhaps the generic and target-specific data
    # should be made available to the template engine as two
    # different instances?
    specific_data = {}
    specific_data.update(generic_data)

    build_commands = ['%configure --disable-static', 'make %{?jobs:-j%jobs}']
    install_commands = ['%makeinstall', 'find %{buildroot} -type f -name "*.la" -delete -print']

    specific_data['BuildCommands'] = build_commands
    specific_data['InstallCommands'] = install_commands

    file_to_package = pkgkit.package_from_file_packagekit_subprocess

    # Resolve dependencies to native packages
    specific_data['Dependencies'] = []
    for dep in generic_data['Dependencies']:
        specific_data['Dependencies'].append(linux.map_dependency(dep, file_to_package))

    specific_data['BuildDependencies'] = []
    for dep in generic_data['BuildDependencies']:
        specific_data['BuildDependencies'].append(linux.map_dependency(dep, file_to_package))

    specific_data['PrepCommands'] = ['%setup -q']
    specific_data['CleanCommands'] = ['rm -rf %{buildroot}']

    specific_data['Files'] = """%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/*"""

    # TODO: only if the package is of type=library or similar
    update_ldconfig = '-p /sbin/ldconfig'
    specific_data['PostUninstall'] = update_ldconfig
    specific_data['PostInstall'] = update_ldconfig

    return specific_data
