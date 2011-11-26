
"""Common code for Linux or Linux-like systems."""

from deploymentkit.core import target, recipe
from deploymentkit.backends import archlinux, rpm

import tarfile, subprocess, os

class LinuxTargetRecipe(recipe.TargetRecipe):
    
    def files(self):
        return self._files

class GeneratorBackend(object):

    supported_targets = [
        target.Target("gnulinux-archlinux-current-x86_64"),
        target.Target("gnulinux-archlinux-current-i686"),
    ]

    def __init__(self):
        pass
        
    def generate_target_recipe(self, generic_recipe, target):
    
        assert target in self.supported_targets
    
        linux_backend = Linux('ArchLinux')
        files = linux_backend.generate_recipe(generic_recipe)
        
        output = LinuxTargetRecipe()
        output._files = files
        
        return output

recipe_generators = {
    'ArchLinux': archlinux.generate_recipe,
    'OpenSUSE': rpm.generate_recipe,
    # 'Fedora': rpm.generate_recipe,
}

installed_file_to_package_mappers = {
    'ArchLinux': archlinux.map_installed_file_to_package,
    'OpenSUSE': rpm.map_installed_file_to_package,
    # 'Fedora': rpm.map_installed_file_to_package,
}

# FIXME: remove public inheritance of TargetPlatform,
# make generic Linux functionality available as helper classes/function
# What we want to share here is the implementation code,
# which is better done through composition
class Linux():
    def __init__(self, distro):

        self._distro = distro

    def generate_recipe(self, pkg_recipe):
        """ """

        # Map target independent values into target specific values.
        target_pkg_recipe = generic_to_specific_recipe(self._distro, pkg_recipe.data)

        # Create the target specific recipe
        generator = recipe_generators[self._distro]
        try:
            output = generator(target_pkg_recipe)
        except KeyError:
            output = {}

        return output



def generic_to_specific_recipe(target, generic_data):
    """Return a mapping representing the target specific recipe data
    based on the @generic_data"""

    # XXX: perhaps the generic and target-specific data
    # should be made available to the template engine as two
    # different instances?
    specific_data = {}
    specific_data.update(generic_data)

    # Add build steps
    if generic_data['BuildSystemType'] != 'autotools':
        # TODO: support other things than autotools
        raise NotImplementedError

    if target == 'ArchLinux':
        build_commands = ['./configure --prefix=/usr', 'make']
        install_commands = ['make DESTDIR="$pkgdir" install']
    else:
        build_commands = ['%configure --disable-static', 'make %{?jobs:-j%jobs}']
        install_commands = ['%makeinstall', 'find %{buildroot} -type f -name "*.la" -delete -print']

    specific_data['BuildCommands'] = build_commands
    specific_data['InstallCommands'] = install_commands

    # Resolve dependencies to native packages
    specific_data['Dependencies'] = []
    for dep in generic_data['Dependencies']:
        specific_data['Dependencies'].append(map_dependency(target, dep))

    specific_data['BuildDependencies'] = []
    for dep in generic_data['BuildDependencies']:
        specific_data['BuildDependencies'].append(map_dependency(target, dep))

    # Target specific
    if target == 'ArchLinux':
        specific_data['SupportedArchitectures'] = ['i686', 'x86_64']

    elif target == 'OpenSUSE':
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

def map_dependency(target, dependency_string):
    dep = dependency_string

    if dep.startswith('pkg-config:'):
        pkgconfig_str = dep.split('pkg-config:')[1]
        pkg_name = package_from_pkgconfig(target, pkgconfig_str)

    elif dep.startswith('executable:'):
        executable_name = dep.split('executable:')[1]
        pkg_name = package_from_executable(target, executable_name)

    else:
        # TODO: support other depencency types
        raise NotImplementedError

    return pkg_name

def package_from_executable(target, executable_name):
    """Return the name of the package that should be used to provide @executable_name"""

    not_installed = subprocess.check_call(['which', executable_name])
    if not_installed:
        # Naive approach:
        # Walk PATH and search in package database for package containing
        # files that matches
        #
        # Problem: some packages will add additional directories
        # to path when installed, with no way to know which ones these are
        # Only real solution here is for packages to have a provides(executable:executable-name)
        # that can be queried from the database. Should then be accesible through PackageKit
        raise NotImplementedError

    executable_path = subprocess.check_output(['which', executable_name]).strip()

    # Target specific
    use_packagekit = True
    if use_packagekit:
        package_id = package_from_file_packagekit_subprocess(executable_path)
    else:
        package_mapper = installed_file_to_package_mappers[target]
        package_id = package_mapper(executable_path)

    return package_id

def package_from_pkgconfig(target, pkg_config_string):
    """Return the name of package that should be used to provide @pkg_config_strig."""

    # TODO: handle version requirements
    pkg_config_id = pkg_config_string

    # TODO: introduce a (target platform) configuration,
    # and define these variables there
    use_packagekit = False
    if use_packagekit:
        return package_from_pkgconfig_packagekit(target, pkg_config_id)
    else:
        return package_from_pkgconfig_fallback(target, pkg_config_id)

def package_from_pkgconfig_packagekit(target, pkg_config_id):

    pkg_config_file = pkg_config_id + '.pc'
    pkg_name = package_from_file_packagekit_subprocess(pkg_config_file)
    return pkg_name

def package_from_file_packagekit_python(filepath):
    # As of 28.08.2011 on Arch Linux the search_file query fails
    # with unable to find dbus method SearchFiles with signature (ss)

    import packagekit.client
    pk_client = packagekit.client.PackageKitClient()
    packages = pk_client.search_file(filepath)

def package_from_file_packagekit_subprocess(filepath):
    output = subprocess.check_output(['pkcon', 'search', 'file', filepath])
    # Output is on the form
    #Transaction:   Searching by name
    #Status:    Querying
    #Package:   gegl-0.1.6-1.x86_64
    #Package:   gegl-gtk-git-20110721-1.x86_64
    #Results:
    #Installed    gegl-0.1.6-1.x86_64
    #Installed    gegl-gtk-git-20110721-1.x86_64

    packages = []
    installed_packages = []
    for line in output.split("\n"):
        if line.startswith('Package:'):
            pkg_id = line.split('Package:')[1].strip()
            packages.append(pkg_id)
        if line.startswith('Installed'):
            pkg_id = line.split('Installed')[1].strip()
            installed_packages.append(pkg_id)

    if len(packages) == 0:
        return ''
    elif len(packages) == 1:
        pkg_id = packages[0]
    else:
        # XXX: Can we handle mutiple packages providing the same file better?
        # FIXME: handle architecture differences correctly
        # TODO: use logging module instead
        print "Warning: Multiple package matches found for pkgconfig identifier %s" % pkg_config_id
        pkg_id = packages[0]


    # Arch Linux specific?
    # Strip away architecture
    # gegl-gtk-git-20110721-1.x86_64 -> gegl-gtk-git-20110721-1
    pkg = pkg_id[0:pkg_id.rindex('.')]

    # Strip away version number
    # Packages are on format:
    # $pkgname-$version-$build_revision
    # where only $pkgname can contain dashes
    # gegl-gtk-git-20110721-1 -> gegl-gtk-git
    pkg_name = '-'.join(pkg.split('-')[0:-2])

    return pkg_name

def package_from_pkgconfig_fallback(target, pkg_config_id):
    # Check if package is installed
    args = ['pkg-config', '--exists', pkg_config_id]
    is_installed = not subprocess.call(args)

    if not is_installed:
        # TODO: look up in package db
        raise NotImplementedError

    # From man pkg-config
    # FIXME: handle lib64 correctly
    # TODO: find a more reliable way to determine the directories
    # * Get a --filename option into pkg-config, perhaps?
    # TODO: handle PKG_CONFIG_LIBDIR and PKG_CONFIG_PATH
    pkg_config_dirs = ['/usr/lib/pkgconfig',
            '/usr/share/pkgconfig',
            '/usr/local/lib/pkgconfig',
            '/usr/local/share/pkgconfig']

    # Search for the .pc file
    package_id = ''
    for dir in pkg_config_dirs:
        filepath = os.path.join(dir, pkg_config_id+'.pc')
        if os.path.exists(filepath):

            # Target specific
            package_mapper = installed_file_to_package_mappers[target]
            package_id = package_mapper(filepath)
            break

    assert package_id, 'Could not find .pc file, but pkg-config said it existed'

    return package_id
