
import tarfile, subprocess, os
import copy

from Cheetah.Template import Template
import yaml

from deploymentkit import core

class ArchLinux(core.TargetPlatform):
#	def __init__(self):
		#core.TargetPlatform.__init__(self)

	def generate_recipe(self, pkg_recipe):
		core.TargetPlatform.generate_recipe(self, pkg_recipe)
		""" """

		# Map target independent values into target specific values.
		target_pkg_recipe = generic_to_specific_recipe(pkg_recipe.data)

		# XXX: perhaps the generic and target-specific data
		# should be made available to the template engine as two
		# different instances?

		# Create the target specific recipe
		pkgbuild = create_pkgbuild(target_pkg_recipe)

		return {'PKGBUILD': pkgbuild}

core.supported_platforms['ArchLinux'] = ArchLinux

def generic_to_specific_recipe(generic_data):
    """Return a mapping representing the target specific recipe data
    based on the @generic_data"""

    # XXX: The output of this is consumed by the template engines
    # for the specific platform. Can we have a well-defined
    # format/interface for all of them, at least for a subset
    # of the properties available?
    specific_data = {}
    specific_data.update(generic_data)

    # FIXME: this is mostly not Arch specific, put somewhere shared

    # Add build steps
    if generic_data['BuildSystemType'] != 'autotools':
                # TODO: support other things than autotools
        raise NotImplementedError

    build_commands = ['./configure --prefix=/usr', 'make']
    install_commands = ['make DESTDIR="$pkgdir" install']

    specific_data['BuildCommands'] = build_commands
    specific_data['InstallCommands'] = install_commands

    # Resolve dependencies to native packages
    specific_data['Dependencies'] = []
    for dep in copy.copy(generic_data['Dependencies']):
        if not dep.startswith('pkg-config:'):
            # TODO: support other deps than pkg-config ones
            raise NotImplementedError

        pkgconfig_str = dep.split('pkg-config:')[1]

        pkg_name = package_from_pkgconfig(pkgconfig_str)
        specific_data['Dependencies'].append(pkg_name)

    # TODO: support this as well
    specific_data['BuildDependencies'] = []

    # Arch Linux specific
    specific_data['SupportedArchitectures'] = ['i686', 'x86_64']


    return specific_data


def package_from_executable(executable_name):
    """Return the name of the package that should be used to provide @executable_name"""
    raise NotImplementedError

def package_from_pkgconfig(pkg_config_string):
    """Return the name of package that should be used to provide @pkg_config_strig."""

    # FIXME: this is mostly not Arch specific, put somewhere shared
    # TODO: Use PackageKit as the primary way of querying this
    # TODO: handle version requirements
    pkg_config_id = pkg_config_string

    # Check if package is installed
    args = ['pkg-config', '--exists', pkg_config_id]
    is_installed = not subprocess.call(args)

    if not is_installed:
        # TODO: look up in package db
        raise NotImplementedError

    # From man pkg-config
    # TODO: find a more reliable way to determine the directories
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

            # Arch Linux specific
            output = subprocess.check_output(['pacman', '-Qo', filepath])
            # Output is on form: "/usr/lib/pkgconfig/sm.pc is owned by libsm 1.2.0-1"
            package_id = output.split()[-2]

            break

    assert package_id, 'Could not find .pc file, but pkg-config said it existed'

    return package_id

def create_pkgbuild(metadata):
    """Return a string representing a PKGBUILD generated from @metadata"""

    # FIXME: don't hardcode
    template_path = 'data/PKGBUILD.tmpl'

    template_definition = open(template_path).read()

    pkgbuild_str = str(Template(template_definition, searchList=metadata))

    return pkgbuild_str

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
