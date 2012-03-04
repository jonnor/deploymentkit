
import os, subprocess

from deploymentkit.core import recipe, target
from deploymentkit.backends import linux, pkgkit, rpm

# FIXME: reduce the code duplication against the opensuse backend code

fedora_versions = ['14', '15', '16']
fedora_architectures = ['i686', 'x86_64']
fedora_series = 'fedora'
fedora_family = 'gnulinux'

fedora_native_buildtoolchain = 'fedora-native'

fedora_supported_targets = []
for version in fedora_versions:
    for arch in fedora_architectures:
        t = target.Target("%s-%s-%s-%s" % (fedora_family, fedora_series, version, arch))
        fedora_supported_targets.append(t)

def is_fedora(target):
    return (target.family == fedora_family and target.series == fedora_series)

class TargetIdentifier(object):

    @staticmethod
    def query():

        # XXX: This is as unreliable/ambigious as detecting a Linux
        # distribution typically is.

        (sysname, nodename, release, version, machine) = os.uname()

        if sysname != 'Linux':
            return None

        if machine in fedora_architectures:
            arch = machine
        else:
            print 'WARNING: Unknown architecture "%s"' % (machine,)

        release_file = '/etc/fedora-release'
        if not os.path.exists(release_file):
            return None

        release = open(release_file).read()
        # Typical output
        """Fedora release 16 (Verne)"""

        tokens = release.split(' ')
        version = tokens[2]
        
        if not version in fedora_versions:
            print 'WARNING: Unknown version "%s"' % (version,)

        t = target.Target()
        t.from_members(fedora_family, fedora_series, version, arch)
        return t

class GeneratorBackend(object):

    supported_targets = fedora_supported_targets

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

        def download_source_files(recipe):
            
            import urllib2
            
            files = {}
            for url in recipe.data['Sources']:
                
                print 'INFO: Downloading source file: %s' % url
                basename = url.split('/')[-1]
                f = urllib2.urlopen(url)
                files[basename] = f.read()
                
            return files

        # rpmbuild requires the sources to be available locally,
        # so we download and add to output files here
        files.update(download_source_files(generic_recipe))

        output = recipe.BuildRecipe()
        output.package_recipe = generic_recipe
        output.files = files.keys()
        output.targets = targets
        output.file_contents = files
        output.toolchain = fedora_native_buildtoolchain

        return output


class BuilderBackend(object):

    supported_targets = fedora_supported_targets
    toolchain = fedora_native_buildtoolchain

    def run(self, build_recipe, targets):
        """ """
        
        spec_file = [path for path in build_recipe.files if path.endswith('.spec')][0]
        sources_dir = os.path.dirname(spec_file) or './'
        
        for target in targets:
            
            if not is_fedora(target):
                raise ValueError, 'Unsupported target: %s' % target

            arch = target.architecture
            if arch == 'i686':
                arch = 'i386'

            distro_version = '%(distro)s-%(version)s-%(arch)s' % \
                {'distro': target.series, 
                'version': target.version,
                'arch': arch}

            common_cmd = ['sudo', 'mock', '-r', distro_version, '--verbose']
            common_cmd.extend(['--no-clean'])

            # Get mock working directoy
            cmd = common_cmd + ['--print-root-path']
            output = subprocess.check_output(cmd)
            # Strip whitespace and remove the last subdirectory (root/)
            mock_workdir = os.path.join(os.path.abspath(output.strip()), os.path.pardir)

            # Build a source RPM
            cmd = common_cmd + ['--buildsrpm', '--spec', spec_file, '--sources', sources_dir]
            print 'INFO: Running command %s' % ' '.join(cmd)
            error_code = subprocess.call(cmd)
            if error_code:
                return False

            # Build the binary RPM
            mock_result_dir = os.path.join(mock_workdir, 'result')
            srpm_path = os.path.join(mock_result_dir, rpm.srpm_name(build_recipe.package_recipe))
            cmd = common_cmd + ['--rebuild',  srpm_path]
            print 'INFO: Running command %s' % ' '.join(cmd)
            error_code = subprocess.call(cmd)
            if error_code:
                return False

        return True

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

    if generic_data['ProjectType'].endswith('application'):
        specific_data['Files'] = """%defattr(-,root,root)
        %{_bindir}/*
        %{_datadir}/*"""

    elif generic_data['ProjectType'] == 'c-library':
        specific_data['Files'] = """%defattr(-,root,root)
        %{_includedir}/*
        %{_libdir}/*"""

    # TODO: only if the package is of type=library or similar
    update_ldconfig = '-p /sbin/ldconfig'
    specific_data['PostUninstall'] = update_ldconfig
    specific_data['PostInstall'] = update_ldconfig

    return specific_data
