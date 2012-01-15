
import tarfile, subprocess, os, tempfile, shutil

from Cheetah.Template import Template
import yaml

from deploymentkit.core import recipe, target
from deploymentkit.backends import linux

archlinux_family = 'gnulinux'
archlinux_series = 'archlinux'
archlinux_versions = ['current']
archlinux_architectures = ['i686', 'x86_64'] # XXX: should architectures be normalized?

archlinux_native_buildtoolchain = 'archlinux-native'

archlinux_supported_targets = [
    target.Target("gnulinux-archlinux-current-x86_64"),
    target.Target("gnulinux-archlinux-current-i686"),
]

def is_archlinux(target):

    return (target.family == archlinux_family and target.series == archlinux_series)
        
class TargetIdentifier(object):
    
    @staticmethod
    def query():

        # XXX: This is as unreliable/ambigious as detecting a Linux
        # distribution typically is.

        (sysname, nodename, release, version, machine) = os.uname()

        if sysname != 'Linux':
            return None
        
        if not os.path.exists('/etc/arch-release'):
            return None
            
        arch = machine

        t = target.Target()
        t.from_members(archlinux_family, archlinux_series, 'current', arch)
        return t


class GeneratorBackend(object):

    supported_targets = archlinux_supported_targets
    
    supported_buildsystems = [
        'autotools',
        'distutils',
    ]

    def __init__(self):
        pass
        
    def generate_build_recipe(self, generic_recipe, targets):
        assert set(targets).intersection(set(self.supported_targets))
    
        # Map target independent values into target specific values.
        target_pkg_recipe = generic_to_specific_recipe(generic_recipe.data)

        # Create the target specific recipe
        try:
            files = generate_recipe(target_pkg_recipe)
        except KeyError:
            files = {}
        
        output = recipe.BuildRecipe()
        output.files = files.keys()
        output.targets = targets
        output.file_contents = files
        output.toolchain = archlinux_native_buildtoolchain
        
        return output

class BuilderBackend(object):

    supported_targets = archlinux_supported_targets
    toolchain = archlinux_native_buildtoolchain
    
    def run(self, build_recipe, targets):
        """ """
        
        for target in targets:
            if not is_archlinux(target):
                raise ValueError, 'Unsupported target: %s' % target


            cmd = ['sudo', 'extra-%s-build' % target.architecture]
            print 'INFO: Running command %s' % ' '.join(cmd)
            subprocess.call(cmd)

class PlatformInfoBackend(object):

    supported_targets = archlinux_supported_targets
    
    def __init__(self):
        pass
        
    def extract(self, target, output_dir):
        arch_extract_platform_info(output_dir, target.to_string())


def generic_to_specific_recipe(generic_data):
    """Return a mapping representing the target specific recipe data
    based on the @generic_data"""

    # XXX: perhaps the generic and target-specific data
    # should be made available to the template engine as two
    # different instances?
    # YES, or more
    # recipe.InputAttribute
    # linux.LinuxSpecificAttribute
    # archlinux.ArchLinuxSpecificAttribute
    
    specific_data = {}
    specific_data.update(generic_data)

    buildsystem_type = generic_data['BuildSystemType']
    if buildsystem_type == 'autotools':
        build_commands = ['./configure --prefix=/usr', 'make']
        install_commands = ['make DESTDIR="$pkgdir" install']

    elif buildsystem_type == 'distutils':
        build_commands = ['']
        if generic_data['ProjectType'].startswith('python2'):
            install_commands  = ['python2 setup.py install --root="$pkgdir/"']
        elif generic_data['ProjectType'].startswith('python3'):
            install_commands  = ['python setup.py install --root="$pkgdir/"']

    if generic_data['ProjectType'].startswith('python2'):
        if not 'executable:python2' in generic_data['Dependencies']:
            generic_data['Dependencies'].append('executable:python2')

    if generic_data['ProjectType'].startswith('python3'):
        if not 'executable:python' in generic_data['Dependencies']:
            generic_data['Dependencies'].append('executable:python')

    specific_data['BuildCommands'] = build_commands
    specific_data['InstallCommands'] = install_commands

    # Resolve dependencies to native packages
    specific_data['Dependencies'] = []
    for dep in generic_data['Dependencies']:
        specific_data['Dependencies'].append(linux.map_dependency(dep, map_installed_file_to_package))

    specific_data['BuildDependencies'] = []
    for dep in generic_data['BuildDependencies']:
        specific_data['BuildDependencies'].append(linux.map_dependency(dep, map_installed_file_to_package))

    specific_data['SupportedArchitectures'] = archlinux_architectures

    return specific_data
    

def generate_recipe(metadata):
    # FIXME: support package.install files
    # for {pre,post}{install,uninstall} targets
    
    pkgbuild = create_pkgbuild(metadata)
    return {'PKGBUILD': pkgbuild}

def map_installed_file_to_package(filename):
    output = subprocess.check_output(['pacman', '-Qo', filename])
    # Output is on form: "/usr/lib/pkgconfig/sm.pc is owned by libsm 1.2.0-1"
    package_id = output.split()[-2]
    
    return package_id

def create_pkgbuild(metadata):
    """Return a string representing a PKGBUILD generated from @metadata"""
    
    # FIXME: don't hardcode
    template_path = 'data/PKGBUILD.tmpl'

    template_definition = open(template_path).read()

    pkgbuild_str = str(Template(template_definition, searchList=metadata))

    return pkgbuild_str

# For retrieving information from repos
def arch_parse_files(files_str):
    lines = files_str.split('\n')

    files = []
    state = 'none'
    for line in lines:
        if not line:
            state = 'none'
            continue
            
        elif '%FILES%' in line:
            state = 'files'
            continue
            
        elif line.startswith('%'):
            state = 'unknown'
            print "Unknown section found: %s" % line
            continue

        if state == 'files':
            files.append(line)

    pkginfo = {'Files': files}
    return pkginfo

def arch_parse_desc(desc_str):
    raise NotImplementedError

    pkginfo = {
        'BriefDescription': desc,
        'URL': url,
    }

    return pkginfo

def arch_parse_depends(deps_str):
    lines = deps_str.split('\n')
    
    deps = []
    provides = []
    optdeps = []
    conflicts = []
    
    state = 'none'
    for line in lines:
        if not line:
            state = 'none'
            continue

        elif '%DEPENDS%' in line:
            state = 'depends'
            continue

        elif '%OPTDEPENDS%' in line:
            state = 'optdepends'
            continue

        elif '%CONFLICTS%' in line:
            state = 'conflicts'
            continue
            
        elif '%PROVIDES%' in line:
            state = 'provides'
            continue
           
        elif line.startswith('%'):
            state = 'unknown'
            print "Unknown section found: %s" % line
            continue
 
        if state == 'depends':
            deps.append(line)
        elif state == 'optdepends':
            optdeps.append(line)
        elif state == 'conflicts':
            conflicts.append(line)
        elif state == 'provides':
            provides.append(line)
        elif state == 'none':
            pass
        else:
            print 'Parser in unknown state: %s' % state
    
    pkginfo = {
        'OptionalDependencies': optdeps,
        'Provides': provides,
        'Conflicts': conflicts,
        'Dependencies': deps,
    }

    return pkginfo

def arch_parse_pkgname(package_name):
    """ """

    split = package_name.split('-') 
    if len(split) < 3:
        raise ValueError, 'invalid package name %s' % (package_name,)

    pkginfo = {
        'Name': '-'.join(split[:-2]),
        'Version': split[-2],
        'Revision': split[-1],
    }

    return pkginfo

def arch_parse_pkg(packages_dir, package_name, detailed=True):
    pkg_info = {}
    pkg_info.update(arch_parse_pkgname(package_name))
        
    def file_content(filename):
        return open(os.path.join(packages_dir, package_name, filename)).read()
        
    if detailed:
        #desc_string = file_content('desc')

        #print desc_string
        #pkg_info.update(arch_parse_desc(desc_string))
        
        files_string = file_content('files')
        pkg_info.update(arch_parse_files(files_string))

        depends_string = file_content('depends')
        pkg_info.update(arch_parse_depends(depends_string))
        
    return pkg_info

def arch_pkglist_from_path(repo_path):
    
    repo_file = tarfile.open(repo_path, 'r:gz')

    tmp_dir = tempfile.mkdtemp()
    repo_file.extractall(tmp_dir)

    packages = {}
    no_packages = len(os.listdir(tmp_dir))
    print "%d packages" % no_packages

    percentage = 0
    for package_no, package_dir in enumerate(os.listdir(tmp_dir)):
        pkg_info = arch_parse_pkg(tmp_dir, package_dir)
        packages[package_dir] = pkg_info
        
        if package_no % no_packages/100 == 0:
            percentage += 1
            print "%s%%" % percentage

    return packages

def arch_pkglist(repository_file_path, output_path, detailed=False):
    """ """

    out_file = open(output_path, 'w')

    packages = arch_pkglist_from_path(repository_file_path)

    # FIXME: this does not make any sense
    # The serialization takes an eternity, 
    # takes a ton of storage, and no-one can consume it directly
    # Instead:
    # - Store and operate on the ArchLinux specific repository info 
    # (pkgfile tarballs)
    # - Convert into a ready-to-consume dependency mapping
    # TODO: set up builders for retrieving repo info at regular intervals
    dumper = yaml.SafeDumper(out_file)
    dumper.open()
    dumper.represent(packages)
    dumper.close()
    
    out_file.close()

def arch_extract_platform_info(output_dir, target_id):
    input_dir = '/var/cache/pkgtools/lists/'

    output_dir = os.path.join(output_dir, target_id)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    repositories = ['core', 'extra', 'community']

    # Extract raw information
    for repo in repositories:
        
        basename = repo + '.files.tar.gz'
        src = os.path.join(input_dir, basename)
        dst = os.path.join(output_dir, basename)
        shutil.copyfile(src, dst)

        
# For testing
def pkgbuild_attribute(pkgbuild, attribute):
    """Return the value of a given @attribute in @pkgbuild.
    The entire value string is returned, or empty string if the attribute is not found.
    NB: Not anywhere close to a decent PKGBUILD parser, only designed to work on
    well-known, super-well-formed input. Used for testing out PKGBUILD generator.
    """

    value = ''

    def parse_attribute_value(line, attribute_name):
        if line.startswith(attribute_name+'='):
            k, v = line.split('=')
            return v

    for line in pkgbuild.split('\n'):
        val = parse_attribute_value(line, attribute)
        if val:
            if value:
                raise ValueError, 'attribute occured twice in PKGBUILD'
            value = val

    return value
